using HNP.GameCore;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace HNP.World
{
    /// <summary>Scene adapter for the prayer contract. It owns only the temporary prayer affordance.</summary>
    public sealed class HnpWorldPrayerInteraction : MonoBehaviour, IHnpInteractable
    {
        [SerializeField] Transform prayerPoint;
        [SerializeField, Min(0.5f)] float activationDistance = 4f;
        [SerializeField, Min(1f)] float prayerDurationSeconds = 3f;

        readonly HnpInteractionOffer offer = new HnpInteractionOffer("phra-pathom-prayer", "ไหว้พระ", HnpInteractionKind.Prayer);
        HnpInteractionSession session = new HnpInteractionSession();
        HnpWorldGame game;
        Button button;
        Text label;
        float completedFeedbackUntil;
        int completedCount;

        [System.Serializable]
        sealed class PrayerSnapshot
        {
            public bool nearby, paused, movementBlocked;
            public string status;
            public float progress;
            public int completedCount;
        }

        void Awake()
        {
            game = FindFirstObjectByType<HnpWorldGame>();
            if (!prayerPoint) prayerPoint = transform;
            CreateButton();
        }

        void Update()
        {
            if (!game || !game.Started) { SetButton(false); return; }
            if (session.Status == HnpInteractionStatus.Active)
            {
                // Prayer must respect all game suspension paths: map, menu, focus and app pause.
                if (game.IsPaused) { SetButton(false); return; }
                session.Tick(Time.deltaTime);
                if (session.Status == HnpInteractionStatus.Completed) Finish(HnpInteractionStatus.Completed);
                else SetButton(true, "กำลังไหว้พระ " + Mathf.CeilToInt((1f - session.PrayerProgress) * prayerDurationSeconds));
                return;
            }
            if (session.Status != HnpInteractionStatus.Idle) session.Reset();
            if (Time.unscaledTime < completedFeedbackUntil) { SetButton(true, "ไหว้พระเสร็จแล้ว"); return; }
            var nearby = Vector3.Distance(game.player.transform.position, prayerPoint.position) <= activationDistance;
            SetButton(nearby, "ไหว้พระ");
            if (nearby && Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame) TryInteract();
        }

        public bool TryGetOffer(out HnpInteractionOffer value) { value = offer; return IsNearby(); }
        public void OnInteractionStarted(HnpInteractionOffer value) { }
        public void OnInteractionFinished(HnpInteractionOffer value, HnpInteractionStatus status) { }

        public void TryInteract()
        {
            if (!IsNearby() || !session.TryBegin(offer, new HnpPrayerDefinition(offer.Id, prayerDurationSeconds))) return;
            game.SetMovementBlocked(true);
            game.pose?.SetPrayerPose(true);
            OnInteractionStarted(offer);
        }

        bool IsNearby() => game && game.Started && !game.IsPaused && prayerPoint && Vector3.Distance(game.player.transform.position, prayerPoint.position) <= activationDistance;
        public void LogPrayerDiagnostics()
        {
            var nearby = game && prayerPoint && Vector3.Distance(game.player.transform.position, prayerPoint.position) <= activationDistance;
            Debug.Log("HNP_PRAYER_QA " + JsonUtility.ToJson(new PrayerSnapshot {
                nearby = nearby, paused = game && game.IsPaused, movementBlocked = game && game.MovementBlocked,
                status = session.Status.ToString(), progress = session.PrayerProgress, completedCount = completedCount
            }));
        }
        void Finish(HnpInteractionStatus status)
        {
            game.SetMovementBlocked(false);
            game.pose?.SetPrayerPose(false);
            if (status == HnpInteractionStatus.Completed) { completedCount++; completedFeedbackUntil = Time.unscaledTime + 1.5f; }
            OnInteractionFinished(offer, status);
            if (status != HnpInteractionStatus.Completed) SetButton(false);
        }

        void CreateButton()
        {
            var canvas = FindFirstObjectByType<Canvas>();
            if (!canvas) return;
            var go = new GameObject("Prayer interaction", typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(canvas.transform, false);
            var rect = (RectTransform)go.transform; rect.anchorMin = rect.anchorMax = new Vector2(1f, 0f); rect.sizeDelta = new Vector2(160, 72); rect.anchoredPosition = new Vector2(-306, 91);
            var image = go.GetComponent<Image>(); image.color = new Color(.55f, .29f, .05f, .96f);
            button = go.GetComponent<Button>(); button.targetGraphic = image; button.onClick.AddListener(TryInteract);
            var text = new GameObject("Label", typeof(RectTransform), typeof(Text)).GetComponent<Text>(); text.transform.SetParent(go.transform, false); text.rectTransform.anchorMin = Vector2.zero; text.rectTransform.anchorMax = Vector2.one; text.rectTransform.sizeDelta = Vector2.zero; text.font = game && game.interfaceFont ? game.interfaceFont : Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); text.fontSize = 24; text.alignment = TextAnchor.MiddleCenter; text.color = new Color(1f, .94f, .77f); text.raycastTarget = false; label = text;
            SetButton(false);
        }

        void SetButton(bool visible, string value = "")
        {
            if (!button) return;
            button.gameObject.SetActive(visible);
            if (label) label.text = value;
        }

        void OnDisable()
        {
            if (game && session.Status == HnpInteractionStatus.Active) { session.Cancel(); game.SetMovementBlocked(false); game.pose?.SetPrayerPose(false); }
        }
    }
}
