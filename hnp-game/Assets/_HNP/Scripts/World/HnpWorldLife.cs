using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace HNP.World {
 public sealed class HnpWorldLife:MonoBehaviour {
  public GameObject[] vehicleModels;public GameObject birdModel,trainModel;public HnpWorldGame game;
  readonly List<Traffic> traffic=new();readonly List<Bird> birds=new();Transform train;float railTime;
  public int VehicleCount=>traffic.Count;public int BirdCount=>birds.Count;
  static readonly Color[] colors={new(.94f,.65f,.08f),new(.13f,.40f,.73f),new(.76f,.11f,.09f),new(.06f,.46f,.34f),new(.86f,.83f,.65f),new(.62f,.16f,.36f)};
  void Start(){if(!game)game=GetComponent<HnpWorldGame>();
   var central=new Route(new[]{new Vector3(-55,.08f,-2.2f),new Vector3(-18,.08f,-2.2f),new Vector3(-16,.08f,0),new Vector3(-18,.08f,2.2f),new Vector3(-55,.08f,2.2f),new Vector3(-57,.08f,0)},1.1f);
   var outer=new Route(new[]{new Vector3(-14.7f,.08f,59.6f),new Vector3(106.5f,.08f,59.6f),new Vector3(106.5f,.08f,-59.6f),new Vector3(-14.7f,.08f,-59.6f)},2.5f);
   if(vehicleModels!=null&&vehicleModels.Length>=4){for(int i=0;i<8;i++)Spawn(i,central,i/8f,3.7f+i*.10f,i%3);for(int i=0;i<10;i++)Spawn(i+8,outer,i/10f,5.2f+i*.12f,i%4);}
   if(birdModel){for(int i=0;i<12;i++){var go=Instantiate(birdModel,transform);go.name="Pigeon "+i;birds.Add(new Bird(go.transform,i));}}
   if(trainModel){train=Instantiate(trainModel,transform).transform;train.name="Station moving train";}
  }
  void Spawn(int i,Route route,float phase,float speed,int type){var go=Instantiate(vehicleModels[type],transform);go.name="Traffic "+i;foreach(var collider in go.GetComponentsInChildren<Collider>())Destroy(collider);
   foreach(var r in go.GetComponentsInChildren<Renderer>()){var list=r.sharedMaterials;for(int j=0;j<list.Length;j++)if(list[j]&&list[j].name.Contains("Body")){var m=new Material(list[j]);m.color=colors[i%colors.Length];list[j]=m;}r.sharedMaterials=list;}
   GetComponent<HnpNightLighting>()?.AttachVehicle(go,type);traffic.Add(new Traffic(go.transform,route,phase,speed));}
  void Update(){if(!game||game.IsPaused)return;float dt=Mathf.Min(Time.deltaTime,.1f);
   foreach(var car in traffic){float gap=car.route.length;foreach(var other in traffic)if(other!=car&&other.route==car.route){float d=Mathf.Repeat(other.distance-car.distance,car.route.length);gap=Mathf.Min(gap,d);}car.Tick(dt,Mathf.Min(car.speed,Mathf.Max(0,(gap-8.2f)*1.7f)));}
   foreach(var bird in birds)bird.Tick(dt,game.Daylight);
   if(train){railTime+=dt;float t=Mathf.PingPong(railTime*2.6f,100);train.position=new(-115,.12f,-50+t);train.rotation=Quaternion.Euler(0,Mathf.Repeat(railTime*2.6f,200)<100?0:180,0);}
  }
  public void LogDiagnostics(){Debug.Log("HNP003_QA "+Diagnostics());}
  public string Diagnostics(){var a=game.visual.GetComponentInChildren<Animator>();var state=a.GetCurrentAnimatorStateInfo(0);return JsonUtility.ToJson(new Snapshot{vehicles=traffic.Count,birds=birds.Count,positions=traffic.Select(t=>t.root.position).ToArray(),birdPositions=birds.Select(b=>b.root.position).ToArray(),wingAngles=birds.Select(b=>b.wingAngle).ToArray(),player=game.player.transform.position,running=game.Running,muted=game.Muted,menu=game.MenuOpen,paused=game.IsPaused,daylight=game.Daylight,animation=state.IsName("Run")?"Run":state.IsName("Walk")?"Walk":"Idle",normalizedTime=state.normalizedTime});}
  [System.Serializable]class Snapshot{public int vehicles,birds;public Vector3[] positions,birdPositions;public float[] wingAngles;public Vector3 player;public bool running,muted,menu,paused;public float daylight,normalizedTime;public string animation;}
  sealed class Route {public readonly Vector3[] points;public readonly float length;public Route(Vector3[] corners,float radius){var p=new List<Vector3>();for(int i=0;i<corners.Length;i++){var a=corners[(i+corners.Length-1)%corners.Length];var b=corners[i];var c=corners[(i+1)%corners.Length];float r=Mathf.Min(radius,Vector3.Distance(a,b)*.35f,Vector3.Distance(b,c)*.35f);var from=b+(a-b).normalized*r;var to=b+(c-b).normalized*r;for(int j=0;j<=8;j++){float t=j/8f;p.Add((1-t)*(1-t)*from+2*(1-t)*t*b+t*t*to);}}points=p.ToArray();for(int i=0;i<points.Length;i++)length+=Vector3.Distance(points[i],points[(i+1)%points.Length]);}
   public Vector3 At(float d){d=Mathf.Repeat(d,length);for(int i=0;i<points.Length;i++){var a=points[i];var b=points[(i+1)%points.Length];float n=Vector3.Distance(a,b);if(d<=n)return Vector3.Lerp(a,b,d/Mathf.Max(.001f,n));d-=n;}return points[0];}}
  sealed class Traffic {public readonly Transform root;public readonly Route route;public readonly float speed;public float distance;readonly Transform[] wheels;public Traffic(Transform t,Route r,float phase,float speed){root=t;route=r;this.speed=speed;distance=phase*r.length;wheels=t.GetComponentsInChildren<Transform>().Where(x=>x.name.StartsWith("Wheel")).ToArray();Tick(0,0);}public void Tick(float dt,float v){distance=Mathf.Repeat(distance+dt*v,route.length);root.position=route.At(distance);root.rotation=Quaternion.LookRotation(route.At(distance+.6f)-root.position);foreach(var wheel in wheels)wheel.Rotate(Vector3.forward,v*dt/.39f*Mathf.Rad2Deg,Space.Self);}}
  sealed class Bird {public readonly Transform root;public float wingAngle;readonly Transform left,right;readonly Quaternion lbase,rbase;Vector3 destination,velocity;float chooseTime,phase;readonly float speed;
   public Bird(Transform root,int i){this.root=root;left=root.GetComponentsInChildren<Transform>().FirstOrDefault(x=>x.name=="Wing_L");right=root.GetComponentsInChildren<Transform>().FirstOrDefault(x=>x.name=="Wing_R");if(left)lbase=left.localRotation;if(right)rbase=right.localRotation;phase=i*.73f;speed=4.5f+i*.15f;root.position=new(-44+i*7,10+i%4*2,-9+i%3*8);velocity=Vector3.forward*speed;Choose();}
   void Choose(){destination=new(Random.Range(-60,90),Random.Range(9,28),Random.Range(-45,45));chooseTime=Random.Range(3,7);}
   public void Tick(float dt,float daylight){chooseTime-=dt;if(chooseTime<0||Vector3.Distance(root.position,destination)<4)Choose();var desired=(destination-root.position).normalized*speed;velocity=Vector3.Lerp(velocity,desired,1-Mathf.Exp(-1.3f*dt));root.position+=velocity*dt;float bank=Vector3.SignedAngle(root.forward,desired,Vector3.up);if(velocity.sqrMagnitude>.01f)root.rotation=Quaternion.Slerp(root.rotation,Quaternion.LookRotation(velocity)*Quaternion.Euler(0,0,Mathf.Clamp(-bank,-25,25)),dt*3);phase+=dt*8;wingAngle=Mathf.Sin(phase)*34;if(left)left.localRotation=lbase*Quaternion.Euler(0,0,-wingAngle);if(right)right.localRotation=rbase*Quaternion.Euler(0,0,wingAngle);}
  }
 }
}
