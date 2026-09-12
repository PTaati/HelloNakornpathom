using UnityEngine;
using UnityEngine.EventSystems;

namespace HNP.Prototype
{
    public sealed class HnpTouchPad : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
    {
        public bool cameraPad;
        public RectTransform knob;
        public Vector2 Value { get; private set; }
        public Vector2 LookDelta { get; private set; }
        int pointer = int.MinValue;
        Vector2 origin;
        public void OnPointerDown(PointerEventData e)
        {
            if (pointer != int.MinValue) return;
            pointer = e.pointerId;
            origin = e.position;
            OnDrag(e);
        }
        public void OnDrag(PointerEventData e)
        {
            if (e.pointerId != pointer) return;
            if (cameraPad) LookDelta += e.delta;
            else
            {
                float radius = 55 * GetComponentInParent<Canvas>().scaleFactor;
                Value = Vector2.ClampMagnitude((e.position-origin)/radius, 1);
                if (knob) knob.anchoredPosition=Value*45;
            }
        }
        public Vector2 ConsumeLook() { var value=LookDelta; LookDelta=Vector2.zero; return value; }
        public void OnPointerUp(PointerEventData e) { if(e.pointerId==pointer) ResetInput(); }
        public void ResetInput()
        {
            pointer=int.MinValue; Value=Vector2.zero; LookDelta=Vector2.zero;
            if(knob) knob.anchoredPosition=Vector2.zero;
        }
        void OnDisable() { ResetInput(); }
    }
}
