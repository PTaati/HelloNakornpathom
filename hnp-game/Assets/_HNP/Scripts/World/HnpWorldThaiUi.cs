using UnityEngine;
using UnityEngine.UI;
namespace HNP.World {
 public sealed class HnpWorldThaiUi : MaskableGraphic {
  public enum Symbol { Menu, Jump, Run, CooldownRing } public Symbol symbol;public float progress;
  public void SetProgress(float value){progress=Mathf.Clamp01(value);SetVerticesDirty();}
  protected override void OnPopulateMesh(VertexHelper vh) {
   vh.Clear();var r=rectTransform.rect;float s=Mathf.Min(r.width,r.height);Vector2 c=r.center;
   Vector2 P(float x,float y)=>c+new Vector2(x,y)*s;
   if(symbol==Symbol.CooldownRing){
    void Arc(float fraction,Color tint){int segments=Mathf.CeilToInt(96*fraction);for(int i=0;i<segments;i++){float a=Mathf.PI*.5f-Mathf.PI*2*i/96;float b=Mathf.PI*.5f-Mathf.PI*2*Mathf.Min((i+1)/96f,fraction);int v=vh.currentVertCount;foreach(var p in new[]{P(Mathf.Cos(a)*.49f,Mathf.Sin(a)*.49f),P(Mathf.Cos(b)*.49f,Mathf.Sin(b)*.49f),P(Mathf.Cos(b)*.445f,Mathf.Sin(b)*.445f),P(Mathf.Cos(a)*.445f,Mathf.Sin(a)*.445f)})vh.AddVert(p,tint,Vector2.zero);vh.AddTriangle(v,v+1,v+2);vh.AddTriangle(v,v+2,v+3);}}
    Arc(1,new Color(.45f,.53f,.48f,.35f));Arc(progress,color);return;
   }
   void Poly(params Vector2[] p){int start=vh.currentVertCount;foreach(var q in p)vh.AddVert(q,color,Vector2.zero);for(int i=1;i<p.Length-1;i++)vh.AddTriangle(start,start+i,start+i+1);}
   void Line(float x,float y,float a,float b,float width=.07f){var p=P(x,y);var q=P(a,b);var n=new Vector2(-(q-p).y,(q-p).x).normalized*s*width/2;Poly(p+n,q+n,q-n,p-n);}
   void Dot(float x,float y,float radius){var pts=new Vector2[14];for(int i=0;i<14;i++){float a=i*Mathf.PI*2/14;pts[i]=P(x+Mathf.Cos(a)*radius,y+Mathf.Sin(a)*radius);}Poly(pts);}
   if(symbol==Symbol.Menu){for(int i=-1;i<=1;i++)Line(-.27f,i*.18f,.27f,i*.18f,.075f);return;}
   if(symbol==Symbol.Jump){Dot(.03f,.23f,.09f);Line(.01f,.10f,-.04f,-.1f);Line(0,.08f,-.23f,.28f);Line(0,.08f,.25f,.30f);Line(-.04f,-.10f,-.20f,-.27f);Line(-.04f,-.1f,.17f,-.23f);Line(-.25f,-.38f,.24f,-.38f,.04f);return;}
   Dot(.14f,.26f,.085f);Line(.08f,.13f,-.04f,-.08f,.09f);Line(.07f,.1f,-.12f,.16f);Line(-.12f,.16f,-.24f,.06f);Line(.04f,.08f,.23f,-.02f);Line(.23f,-.02f,.32f,.1f);Line(-.04f,-.08f,.12f,-.22f);Line(.12f,-.22f,.30f,-.20f);Line(-.04f,-.08f,-.20f,-.25f);Line(-.20f,-.25f,-.28f,-.36f);Line(-.39f,.20f,-.22f,.20f,.025f);Line(-.42f,.10f,-.30f,.10f,.025f);
  }
 }
}
