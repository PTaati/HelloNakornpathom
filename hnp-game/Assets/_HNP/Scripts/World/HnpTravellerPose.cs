using UnityEngine;
namespace HNP.World {
 public sealed class HnpTravellerPose : MonoBehaviour {
  public Transform leftArm,rightArm,leftLeg,rightLeg,head;
 Quaternion la,ra,ll,rl,hh; float phase,blend,smoothedSpeed; bool praying;
  void Awake(){la=leftArm.localRotation;ra=rightArm.localRotation;ll=leftLeg.localRotation;rl=rightLeg.localRotation;hh=head.localRotation;}
 public void Animate(float speed,bool grounded,float dt){
   if(praying){leftArm.localRotation=Quaternion.Slerp(leftArm.localRotation,la*Quaternion.Euler(-58,0,-28),1-Mathf.Exp(-12*dt));rightArm.localRotation=Quaternion.Slerp(rightArm.localRotation,ra*Quaternion.Euler(-58,0,28),1-Mathf.Exp(-12*dt));leftLeg.localRotation=ll;rightLeg.localRotation=rl;head.localRotation=hh*Quaternion.Euler(10,0,0);return;}
   // Actual controller displacement can briefly be zero on a slope/collider.  Filter it so
   // procedural limbs settle naturally instead of visibly snapping between walk and idle.
   smoothedSpeed=Mathf.MoveTowards(smoothedSpeed,speed,dt*(speed>smoothedSpeed?16f:7f));
   blend=Mathf.MoveTowards(blend,grounded?Mathf.Clamp01(smoothedSpeed/2.1f):0,dt*7);phase+=dt*Mathf.Lerp(0,11,Mathf.Clamp01(smoothedSpeed/6));
   float swing=Mathf.Sin(phase)*28*blend;
   leftArm.localRotation=la*Quaternion.Euler(grounded?-swing:-25,0,-3);
   rightArm.localRotation=ra*Quaternion.Euler(grounded?swing:-25,0,3);
   leftLeg.localRotation=ll*Quaternion.Euler(grounded?swing:15,0,0);
   rightLeg.localRotation=rl*Quaternion.Euler(grounded?-swing:-12,0,0);
  head.localRotation=hh*Quaternion.Euler(0,Mathf.Sin(Time.time*1.4f)*2,0);
 }
 public void SetPrayerPose(bool value){praying=value;}
 }
}
