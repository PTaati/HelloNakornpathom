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
                session.Tick(Time.deltaTime);
                if (session.Status == HnpInteractionStatus.Completed) Finish(HnpInteractionStatus.Completed);
                else SetButton(true, "กำลังไหว้พระ " + Mathf.CeilToInt((1f - session.PrayerProgress) * prayerDurationSeconds));
                return;
            }
            if (session.Status != HnpInteractionStatus.Idle) session.Reset();
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
            OnInteractionStarted(offer);
        }

        bool IsNearby() => game && game.Started && prayerPoint && Vector3.Distance(game.player.transform.position, prayerPoint.position) <= activationDistance;
        void Finish(HnpInteractionStatus status)
        {
            game.SetMovementBlocked(false);
            OnInteractionFinished(offer, status);
            SetButton(false);
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
            var text = new GameObject("Label", typeof(RectTransform), typeof(Text)).GetComponent<Text>(); text.transform.SetParent(go.transform, false); text.rectTransform.anchorMin = Vector2.zero; text.rectTransform.anchorMax = Vector2.one; text.rectTransform.sizeDelta = Vector2.zero; text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); text.fontSize = 24; text.alignment = TextAnchor.MiddleCenter; text.color = new Color(1f, .94f, .77f); text.raycastTarget = false; label = text;
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
            if (game && session.Status == HnpInteractionStatus.Active) { session.Cancel(); game.SetMovementBlocked(false); }
        }
    }
}
