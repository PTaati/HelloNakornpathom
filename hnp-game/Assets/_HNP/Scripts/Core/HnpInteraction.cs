using System;

namespace HNP.GameCore
{
    public enum HnpInteractionKind
    {
        None,
        Prayer,
        Dialogue,
        Collect,
        Minigame,
        Boarding
    }

    public enum HnpInteractionStatus
    {
        Idle,
        Active,
        Completed,
        Cancelled
    }

    /// <summary>Data returned by a nearby world target. The target owns presentation and rewards.</summary>
    public struct HnpInteractionOffer
    {
        public string Id;
        public string Prompt;
        public HnpInteractionKind Kind;

        public HnpInteractionOffer(string id, string prompt, HnpInteractionKind kind)
        {
            Id = id;
            Prompt = prompt;
            Kind = kind;
        }

        public bool IsValid => !string.IsNullOrWhiteSpace(Id) && Kind != HnpInteractionKind.None;
    }

    /// <summary>Scene targets implement this small contract; target discovery stays outside the core.</summary>
    public interface IHnpInteractable
    {
        bool TryGetOffer(out HnpInteractionOffer offer);
        void OnInteractionStarted(HnpInteractionOffer offer);
        void OnInteractionFinished(HnpInteractionOffer offer, HnpInteractionStatus status);
    }

    public struct HnpPrayerDefinition
    {
        public string Id;
        public float DurationSeconds;

        public HnpPrayerDefinition(string id, float durationSeconds)
        {
            Id = id;
            DurationSeconds = Math.Max(0.01f, durationSeconds);
        }

        public bool IsValid => !string.IsNullOrWhiteSpace(Id) && DurationSeconds > 0f;
    }

    /// <summary>One active interaction at a time. A prayer completes from elapsed active game time.</summary>
    public sealed class HnpInteractionSession
    {
        public HnpInteractionOffer ActiveOffer { get; private set; }
        public HnpInteractionStatus Status { get; private set; } = HnpInteractionStatus.Idle;
        public float PrayerProgress { get; private set; }
        public bool BlocksLocomotion => Status == HnpInteractionStatus.Active && ActiveOffer.Kind == HnpInteractionKind.Prayer;

        float prayerDuration;

        public bool TryBegin(HnpInteractionOffer offer, HnpPrayerDefinition prayer)
        {
            if (Status != HnpInteractionStatus.Idle || !offer.IsValid)
            {
                return false;
            }

            if (offer.Kind == HnpInteractionKind.Prayer && (!prayer.IsValid || prayer.Id != offer.Id))
            {
                return false;
            }

            ActiveOffer = offer;
            Status = HnpInteractionStatus.Active;
            PrayerProgress = 0f;
            prayerDuration = offer.Kind == HnpInteractionKind.Prayer ? prayer.DurationSeconds : 0f;
            return true;
        }

        public void Tick(float unscaledGameplayDeltaSeconds)
        {
            if (Status != HnpInteractionStatus.Active || ActiveOffer.Kind != HnpInteractionKind.Prayer)
            {
                return;
            }

            PrayerProgress = Math.Min(1f, PrayerProgress + Math.Max(0f, unscaledGameplayDeltaSeconds) / prayerDuration);
            if (PrayerProgress >= 1f)
            {
                Status = HnpInteractionStatus.Completed;
            }
        }

        public bool Complete()
        {
            if (Status != HnpInteractionStatus.Active)
            {
                return false;
            }

            PrayerProgress = ActiveOffer.Kind == HnpInteractionKind.Prayer ? 1f : PrayerProgress;
            Status = HnpInteractionStatus.Completed;
            return true;
        }

        public bool Cancel()
        {
            if (Status != HnpInteractionStatus.Active)
            {
                return false;
            }

            Status = HnpInteractionStatus.Cancelled;
            return true;
        }

        public void Reset()
        {
            ActiveOffer = default(HnpInteractionOffer);
            Status = HnpInteractionStatus.Idle;
            PrayerProgress = 0f;
            prayerDuration = 0f;
        }
    }
}
