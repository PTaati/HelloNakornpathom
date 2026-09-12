using UnityEngine;

namespace HNP.World {
 /// <summary>Feeds the imported rig's in-place Idle/Walk controller from the existing CharacterController.</summary>
 public sealed class HnpTravellerAnimatorBridge : MonoBehaviour {
  public CharacterController controller;
  Animator animator;HnpWorldGame game;Vector3 previous;
  static readonly int Speed = Animator.StringToHash("Speed");
  void Awake(){animator=GetComponentInChildren<Animator>();game=FindAnyObjectByType<HnpWorldGame>();if(controller)previous=controller.transform.position;}
  void LateUpdate(){if(!controller||!animator)return;var delta=controller.transform.position-previous;previous=controller.transform.position;delta.y=0;float speed=delta.magnitude/Mathf.Max(Time.deltaTime,.001f);bool fast=game&&game.Running;speed=speed>.15f?(fast?HnpWorldGame.RunSpeed:HnpWorldGame.WalkSpeed):0;if(speed==0){animator.SetFloat(Speed,0);if(!animator.GetCurrentAnimatorStateInfo(0).IsName("Idle")||animator.IsInTransition(0)){animator.Play("Idle",0,0);animator.Update(0);}}else animator.SetFloat(Speed,speed,.06f,Time.deltaTime);}
 }
}
