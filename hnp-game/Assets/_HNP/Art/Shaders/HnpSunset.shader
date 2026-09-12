Shader "HNP/SunsetSky" {
 Properties { _Top("Sky",Color)=(0.64,0.44,0.37,1) _Horizon("Horizon",Color)=(1,0.76,0.39,1) _Daylight("Daylight",Range(0,1))=1 _SunDirection("Sun direction",Vector)=(.94,.24,-.30,0) }
 SubShader { Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" } Cull Off ZWrite Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct appdata {float4 vertex:POSITION;};struct v2f {float4 position:SV_POSITION;float3 dir:TEXCOORD0;};
 float4 _Top,_Horizon,_SunDirection;float _Daylight;
 v2f vert(appdata v){v2f o;o.position=UnityObjectToClipPos(v.vertex);o.dir=v.vertex.xyz;return o;}
 float hash(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453);}
 float noise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y);}
 fixed4 frag(v2f i):SV_Target {float3 d=normalize(i.dir);float t=saturate(d.y*1.6);float3 c=lerp(_Horizon.rgb,_Top.rgb,pow(t,.65));float sun=dot(d,normalize(_SunDirection.xyz));c+=float3(1,.63,.23)*pow(saturate(sun),18)*.25*_Daylight;c=lerp(c,float3(1,.94,.65),smoothstep(.9978,.9992,sun)*_Daylight);float2 uv=float2(atan2(d.z,d.x)*2.0,d.y*14.0);float n=noise(uv*2)+noise(uv*4)*.4;float cloud=smoothstep(.74,1.05,n)*smoothstep(.015,.14,d.y)*(1-smoothstep(.55,.88,d.y));c=lerp(c,lerp(float3(.035,.05,.10),float3(.98,.63,.43),_Daylight),cloud*.24);return float4(c,1);}
 ENDCG }
 } Fallback Off
}
