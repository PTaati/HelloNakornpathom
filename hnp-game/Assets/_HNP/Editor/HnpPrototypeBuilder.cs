using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEditor.Build.Reporting;
using HNP.Prototype;

namespace HNP.Editor
{
    public static class HnpPrototypeBuilder
    {
        public const string ScenePath="Assets/_HNP/Scenes/StationPrototype.unity";
        const string Art="Assets/_HNP/Art/";
        static Material cream, teal, wood, gold, dark, green, stone, red;
        static string Root=>Directory.GetParent(Application.dataPath).Parent.FullName;
        static Material Mat(string name,Color color)
        {
            var path=Art+"Materials/"+name+".mat";
            var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!m) { m=new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(m,path); }
            m.color=color; m.SetFloat("_Smoothness",.12f); EditorUtility.SetDirty(m); return m;
        }
        static GameObject Shape(string name,PrimitiveType type,Vector3 pos,Vector3 scale,Material mat,Transform parent=null,bool collider=true)
        {
            var go=GameObject.CreatePrimitive(type); go.name=name; go.transform.SetParent(parent,false);
            go.transform.localPosition=pos; go.transform.localScale=scale; go.GetComponent<Renderer>().sharedMaterial=mat;
            if(!collider) UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());
            return go;
        }
        static GameObject Box(string n,Vector3 p,Vector3 s,Material m,Transform parent=null,bool collider=true)=>Shape(n,PrimitiveType.Cube,p,s,m,parent,collider);
        static void Sign(string text,Vector3 p,float size,Color color,Transform parent=null)
        {
            var go=new GameObject("Sign "+text); go.transform.SetParent(parent,false); go.transform.localPosition=p;
            go.transform.localRotation=Quaternion.identity;
            var label=go.AddComponent<TextMesh>(); label.text=text; label.fontSize=64; label.characterSize=size*.5f;
            label.anchor=TextAnchor.MiddleCenter; label.alignment=TextAlignment.Center; label.color=color;
        }
        [MenuItem("HNP/Create Station Prototype")]
        public static void Create()
        {
            if(EditorApplication.isPlaying) throw new InvalidOperationException("Exit Play Mode before creating a scene.");
            for(int i=0;i<SceneManager.sceneCount;i++) if(SceneManager.GetSceneAt(i).isDirty) throw new InvalidOperationException("Save existing scene edits before creating prototype.");
            if(File.Exists(ScenePath)) throw new InvalidOperationException("Prototype scene already exists; open it instead of overwriting.");
            Directory.CreateDirectory(Art+"Materials"); Directory.CreateDirectory("Assets/_HNP/Prefabs"); Directory.CreateDirectory("Assets/_HNP/Scenes");
            AssetDatabase.Refresh();
            cream=Mat("HNP_Cream",new Color(.92f,.83f,.63f)); teal=Mat("HNP_DeepTeal",new Color(.035f,.22f,.23f));
            wood=Mat("HNP_Teak",new Color(.42f,.19f,.065f)); gold=Mat("HNP_Gold",new Color(1,.64f,.13f));
            dark=Mat("HNP_Ink",new Color(.09f,.12f,.14f)); green=Mat("HNP_Green",new Color(.28f,.46f,.28f));
            stone=Mat("HNP_Stone",new Color(.68f,.62f,.49f)); red=Mat("HNP_Roof",new Color(.55f,.19f,.10f));
            var modelPath=Art+"Models/HNP_Prop_StationBench_A.fbx";
            var importer=AssetImporter.GetAtPath(modelPath) as ModelImporter;
            if(!importer) throw new InvalidOperationException("Blender FBX is missing.");
            importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
            importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),"HNP_Teak"),wood);
            importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),"HNP_DeepTeal"),teal);
            importer.SaveAndReimport();
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var env=new GameObject("Station environment").transform;
            Box("Platform",new Vector3(0,-.3f,0),new Vector3(26,.6f,44),stone,env);
            Box("Lawn",new Vector3(0,-.65f,15),new Vector3(100,.5f,130),green,env);
            Box("Safety line",new Vector3(-7.6f,.015f,0),new Vector3(.15f,.025f,43),gold,env,false);
            for(int i=-10;i<=10;i++) Box("Paving seam",new Vector3(1,.012f,i*2),new Vector3(16,.02f,.025f),cream,env,false);
            for(int x=-11;x<=-9;x+=2) Box("Rail",new Vector3(x,-.08f,0),new Vector3(.13f,.15f,55),dark,env);
            for(int z=-25;z<=25;z+=2) Box("Sleeper",new Vector3(-10,-.18f,z),new Vector3(3,.14f,.35f),wood,env);
            Box("Station building",new Vector3(8,2.3f,0),new Vector3(6,4.6f,18),cream,env);
            Box("Station foundation",new Vector3(8,.2f,0),new Vector3(6.5f,.4f,18.5f),teal,env);
            for(int z=-6;z<=6;z+=4)
            {
                Box("Window frame",new Vector3(4.97f,2.1f,z),new Vector3(.08f,1.9f,2.1f),wood,env);
                Box("Window glass",new Vector3(4.91f,2.1f,z),new Vector3(.04f,1.55f,1.75f),teal,env);
            }
            for(int side=-1;side<=1;side+=2)
            {
                var roof=Box("Pitched station roof",new Vector3(8+side*1.6f,5.35f,0),new Vector3(4,.22f,20),red,env);
                roof.transform.localRotation=Quaternion.Euler(0,0,-side*24);
            }
            for(int z=-8;z<=8;z+=8) for(int x=-6;x<=2;x+=8)
                Box("Canopy column",new Vector3(x,1.85f,z),new Vector3(.23f,3.7f,.23f),teal,env);
            Box("Platform canopy",new Vector3(-2,3.85f,0),new Vector3(9,.22f,20),cream,env);
            Box("Canopy fascia",new Vector3(-2,3.65f,-10),new Vector3(9,.45f,.15f),teal,env);
            Sign("NAKORNPATHOM",new Vector3(-2,3.65f,-10.1f),.14f,Color.white,env);
            for(int z=-13;z<=13;z+=26)
            {
                Box("Planter",new Vector3(8,.35f,z),new Vector3(2,.7f,2),cream,env);
                Shape("Tree trunk",PrimitiveType.Cylinder,new Vector3(8,1.5f,z),new Vector3(.4f,1.3f,.4f),wood,env);
                Shape("Tree crown",PrimitiveType.Sphere,new Vector3(8,3.2f,z),new Vector3(3.2f,3.8f,3.2f),green,env,false);
            }
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var benchRoot=new GameObject("HNP Station Bench");
            var bench=(GameObject)PrefabUtility.InstantiatePrefab(model); bench.transform.SetParent(benchRoot.transform,false);
            var seat=benchRoot.AddComponent<BoxCollider>(); seat.center=new Vector3(0,.25f,0); seat.size=new Vector3(1.8f,.5f,.65f);
            var back=benchRoot.AddComponent<BoxCollider>(); back.center=new Vector3(0,.85f,.30f); back.size=new Vector3(1.8f,.6f,.12f);
            var prefab=PrefabUtility.SaveAsPrefabAsset(benchRoot,"Assets/_HNP/Prefabs/StationBench.prefab");
            benchRoot.transform.position=new Vector3(3.7f,0,-5); benchRoot.transform.rotation=Quaternion.Euler(0,-90,0);
            var second=(GameObject)PrefabUtility.InstantiatePrefab(prefab); second.transform.position=new Vector3(3.7f,0,6); second.transform.rotation=Quaternion.Euler(0,-90,0);
            var train=new GameObject("Arrival train").transform; train.position=new Vector3(-10,0,0);
            Box("Carriage",new Vector3(0,1.65f,0),new Vector3(2.6f,2.2f,15),cream,train);
            Box("Train lower stripe",new Vector3(0,.75f,0),new Vector3(2.68f,.5f,15.1f),teal,train);
            Box("Train roof",new Vector3(0,2.95f,0),new Vector3(2.8f,.35f,15.3f),red,train);
            for(int z=-6;z<=6;z+=3) for(int side=-1;side<=1;side+=2)
                Box("Train window",new Vector3(side*1.31f,2,z),new Vector3(.03f,.85f,1.75f),teal,train,false);
            for(int z=-5;z<=5;z+=10) for(int side=-1;side<=1;side+=2)
            { var wheel=Shape("Wheel",PrimitiveType.Cylinder,new Vector3(side*1.05f,.38f,z),new Vector3(.8f,.14f,.8f),dark,train,false); wheel.transform.localRotation=Quaternion.Euler(0,0,90); }
            // Distant provisional landmark gives a visual direction for the next production stage.
            for(int i=0;i<7;i++) Shape("Chedi stepped silhouette",PrimitiveType.Cylinder,new Vector3(0,i*.65f+.3f,46),new Vector3(12-i*1.3f,.4f,12-i*1.3f),gold,env,false);
            Shape("Chedi spire",PrimitiveType.Cylinder,new Vector3(0,6.5f,46),new Vector3(.6f,2.2f,.6f),gold,env,false);
            var gate=new GameObject("Departure arch").transform; gate.position=new Vector3(0,0,17);
            for(int side=-1;side<=1;side+=2) Box("Arch post",new Vector3(side*2.1f,1.75f,0),new Vector3(.3f,3.5f,.3f),teal,gate);
            Box("Arch sign",new Vector3(0,3.4f,0),new Vector3(4.6f,.75f,.3f),teal,gate);
            Sign("TO THE FAIR",new Vector3(0,3.4f,-.18f),.17f,Color.white,gate);
            // Edge barriers keep the starter area playable.
            Box("West boundary",new Vector3(-12.8f,1,0),new Vector3(.25f,2,44),teal,env);
            Box("South boundary",new Vector3(0,1,-21.8f),new Vector3(26,2,.25f),teal,env);
            Box("East boundary",new Vector3(12.8f,1,0),new Vector3(.25f,2,44),teal,env);
            Box("North boundary",new Vector3(0,.5f,21.8f),new Vector3(26,1,.25f),teal,env);
            var player=new GameObject("Traveller"); player.layer=2; player.transform.position=new Vector3(0,.1f,-14);
            var controller=player.AddComponent<CharacterController>(); controller.height=1.8f; controller.radius=.3f; controller.center=new Vector3(0,.9f,0); controller.stepOffset=.3f;
            var visual=new GameObject("Traveller visual").transform; visual.SetParent(player.transform,false);
            Shape("Shirt",PrimitiveType.Capsule,new Vector3(0,1,0),new Vector3(.55f,.40f,.4f),cream,visual,false);
            Shape("Head",PrimitiveType.Sphere,new Vector3(0,1.59f,0),Vector3.one*.37f,wood,visual,false);
            Shape("Hat brim",PrimitiveType.Cylinder,new Vector3(0,1.79f,0),new Vector3(.65f,.035f,.55f),gold,visual,false);
            Shape("Hat crown",PrimitiveType.Cylinder,new Vector3(0,1.88f,0),new Vector3(.37f,.08f,.34f),wood,visual,false);
            for(int side=-1;side<=1;side+=2)
            {
                Box("Shorts",new Vector3(side*.14f,.58f,0),new Vector3(.23f,.4f,.3f),dark,visual,false);
                Box("Leg",new Vector3(side*.14f,.26f,0),new Vector3(.14f,.3f,.16f),wood,visual,false);
                Box("Sandal",new Vector3(side*.14f,.08f,.05f),new Vector3(.2f,.1f,.32f),dark,visual,false);
            }
            var cameraGO=new GameObject("Main Camera",typeof(Camera),typeof(AudioListener)); cameraGO.tag="MainCamera";
            var cam=cameraGO.GetComponent<Camera>(); cam.fieldOfView=55; cam.farClipPlane=160; cam.clearFlags=CameraClearFlags.SolidColor; cam.backgroundColor=new Color(.71f,.82f,.80f);
            var sun=new GameObject("Late afternoon sun",typeof(Light)); sun.transform.rotation=Quaternion.Euler(48,-35,0);
            var light=sun.GetComponent<Light>(); light.type=LightType.Directional; light.intensity=1.5f; light.color=new Color(1,.88f,.68f); light.shadows=LightShadows.Soft;
            RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight=new Color(.62f,.69f,.71f);
            RenderSettings.fog=true; RenderSettings.fogColor=cam.backgroundColor; RenderSettings.fogMode=FogMode.Linear; RenderSettings.fogStartDistance=45; RenderSettings.fogEndDistance=135;
            var game=new GameObject("HNP Station Game").AddComponent<HnpStationGame>();
            game.player=controller; game.visual=visual; game.gameCamera=cam; game.train=train; game.destination=gate;
            var positions=new[]{new Vector3(0,1,-6),new Vector3(-3,1,3),new Vector3(1,1,11)};
            game.postcards=new Transform[positions.Length];
            for(int i=0;i<positions.Length;i++)
            {
                var card=Box("Golden postcard "+(i+1),positions[i],new Vector3(.65f,.45f,.12f),gold,null,false);
                game.postcards[i]=card.transform;
                Box("Card seal",new Vector3(0,0,-.08f),new Vector3(.36f,.23f,.03f),cream,card.transform,false);
                Shape("Marker base",PrimitiveType.Cylinder,new Vector3(positions[i].x,.025f,positions[i].z),new Vector3(1.1f,.025f,1.1f),gold,env,false);
            }
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene,ScenePath); AssetDatabase.SaveAssets();
            Selection.activeGameObject=player;
            if(SceneView.lastActiveSceneView) SceneView.lastActiveSceneView.LookAt(new Vector3(0,1,0),Quaternion.Euler(30,20,0),25);
            Debug.Log("HNP_CREATE_PASS: " + ScenePath);
        }
        [MenuItem("HNP/Build Web Prototype")]
        public static void BuildWeb()
        {
            if(EditorApplication.isPlaying) throw new InvalidOperationException("Exit Play Mode before building.");
            Directory.CreateDirectory(Path.Combine(Root,"reports"));
            var mobilePipeline=AssetDatabase.LoadAssetAtPath<UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");
            if(!mobilePipeline) throw new InvalidOperationException("Mobile URP asset missing.");
            UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline=mobilePipeline;
            QualitySettings.SetQualityLevel(0,true);
            QualitySettings.renderPipeline=mobilePipeline;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.WebGL,false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.WebGL,new[]{UnityEngine.Rendering.GraphicsDeviceType.OpenGLES3});
            AssetDatabase.SaveAssets();
            PlayerSettings.WebGL.template="PROJECT:HNP";
            PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Disabled;
            PlayerSettings.defaultWebScreenWidth=1280; PlayerSettings.defaultWebScreenHeight=720;
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes=new[]{ScenePath},
                locationPathName=Path.Combine(Root,"builds/web"), target=BuildTarget.WebGL, options=BuildOptions.None });
            var s=report.summary;
            File.WriteAllText(Path.Combine(Root,"reports/web-build.txt"),$"Result: {s.result}\nErrors: {s.totalErrors}\nWarnings: {s.totalWarnings}\nBytes: {s.totalSize}\nTime: {s.totalTime}\n");
            if(s.result!=BuildResult.Succeeded) throw new Exception("Web build failed: "+s.result);
        }
    }
}
