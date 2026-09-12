using NUnit.Framework;
using UnityEngine;

namespace HNP.GameCore.Tests
{
    public sealed class HnpGameCoreTests
    {
        static readonly HnpLocomotionSettings Movement = new HnpLocomotionSettings(3f, 6f, 0.1f);

        [Test]
        public void Locomotion_ClampsDiagonalInput_AndUsesWalkSpeed()
        {
            var result = HnpLocomotionResolver.Resolve(new HnpLocomotionInput(new Vector2(2f, 2f), false), Movement, true);

            Assert.That(result.Mode, Is.EqualTo(HnpLocomotionMode.Walk));
            Assert.That(result.Speed, Is.EqualTo(3f));
            Assert.That(result.Direction.magnitude, Is.EqualTo(1f).Within(0.0001f));
        }

        [Test]
        public void Locomotion_BlocksRun_WhenMovementIsNotAllowed()
        {
            var result = HnpLocomotionResolver.Resolve(new HnpLocomotionInput(Vector2.up, true), Movement, false);

            Assert.That(result.Mode, Is.EqualTo(HnpLocomotionMode.Idle));
            Assert.That(result.Speed, Is.Zero);
        }

        [Test]
        public void Prayer_CompletesOnlyAfterItsConfiguredActiveDuration()
        {
            var session = new HnpInteractionSession();
            var offer = new HnpInteractionOffer("chedi-prayer", "Pay respect", HnpInteractionKind.Prayer);

            Assert.That(session.TryBegin(offer, new HnpPrayerDefinition("chedi-prayer", 4f)), Is.True);
            session.Tick(3.99f);
            Assert.That(session.Status, Is.EqualTo(HnpInteractionStatus.Active));
            Assert.That(session.PrayerProgress, Is.LessThan(1f));

            session.Tick(0.01f);
            Assert.That(session.Status, Is.EqualTo(HnpInteractionStatus.Completed));
            Assert.That(session.PrayerProgress, Is.EqualTo(1f));
        }

        [Test]
        public void Prayer_BlocksLocomotion_AndCanBeCancelled()
        {
            var session = new HnpInteractionSession();
            var offer = new HnpInteractionOffer("chedi-prayer", "Pay respect", HnpInteractionKind.Prayer);
            session.TryBegin(offer, new HnpPrayerDefinition("chedi-prayer", 4f));

            Assert.That(session.BlocksLocomotion, Is.True);
            Assert.That(session.Cancel(), Is.True);
            Assert.That(session.Status, Is.EqualTo(HnpInteractionStatus.Cancelled));
            Assert.That(session.BlocksLocomotion, Is.False);
        }

        [Test]
        public void Interaction_RejectsASecondActiveOffer_AndMismatchedPrayerData()
        {
            var session = new HnpInteractionSession();
            var prayer = new HnpInteractionOffer("chedi-prayer", "Pay respect", HnpInteractionKind.Prayer);
            var dialogue = new HnpInteractionOffer("vendor", "Talk", HnpInteractionKind.Dialogue);

            Assert.That(session.TryBegin(prayer, new HnpPrayerDefinition("other", 2f)), Is.False);
            Assert.That(session.TryBegin(prayer, new HnpPrayerDefinition("chedi-prayer", 2f)), Is.True);
            Assert.That(session.TryBegin(dialogue, default(HnpPrayerDefinition)), Is.False);
        }

        [Test]
        public void Interaction_RequiresResetAfterCompletion_SoTheResultCanBeConsumed()
        {
            var session = new HnpInteractionSession();
            var dialogue = new HnpInteractionOffer("vendor", "Talk", HnpInteractionKind.Dialogue);

            Assert.That(session.TryBegin(dialogue, default(HnpPrayerDefinition)), Is.True);
            Assert.That(session.Complete(), Is.True);
            Assert.That(session.TryBegin(dialogue, default(HnpPrayerDefinition)), Is.False);
            session.Reset();
            Assert.That(session.TryBegin(dialogue, default(HnpPrayerDefinition)), Is.True);
        }
    }
}
