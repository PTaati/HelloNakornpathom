using UnityEngine;

namespace HNP.World {
 /// <summary>Small mobile-Web culling helper for repeated world kits.</summary>
 public sealed class HnpDistanceVisibility : MonoBehaviour {
  [SerializeField] float visibleDistance = 180f;
  [SerializeField] float hysteresis = 15f;
  Transform target;
  Renderer[] renderers;
  bool visible = true;
  void Awake() { renderers = GetComponentsInChildren<Renderer>(true); var game = FindFirstObjectByType<HnpWorldGame>(); target = game ? game.player.transform : Camera.main ? Camera.main.transform : null; }
  void Update() {
   if (!target || renderers == null) return;
   float limit = visible ? visibleDistance + hysteresis : visibleDistance;
   bool next = (target.position - transform.position).sqrMagnitude <= limit * limit;
   if (next == visible) return;
   visible = next;
   foreach (var renderer in renderers) if (renderer) renderer.enabled = visible;
  }
 }
}
