using UnityEngine;
using UnityEngine.UI;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.EventSystems;

namespace HNP.Prototype
{
    public sealed class HnpStationGame : MonoBehaviour
    {
        public CharacterController player;
        public Transform visual;
        public Camera gameCamera;
        public Transform[] postcards;
        public Transform destination;
        public Transform train;
        public int Collected { get; private set; }
        public bool Finished { get; private set; }
        public bool Started { get; private set; }
        public float VerticalSpeed => verticalSpeed;
        Vector3 spawn;
        Vector3 trainHome;
        float yaw, pitch=25, verticalSpeed, arrivalTime;
        bool jumpRequested, interactRequested, focused=true;
        HnpTouchPad movePad, lookPad;
        Text objective, prompt, counter;
        GameObject startPanel, endPanel, rotatePanel;
        RectTransform safeRoot;
        bool[] picked;
        Font font;

        void Awake()
        {
            spawn=player.transform.position;
            trainHome=train.position;
            picked=new bool[postcards.Length];
            font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            Application.targetFrameRate=60;
            Debug.Log("HNP runtime: quality="+QualitySettings.GetQualityLevel()+" pipeline="+UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline+" api="+SystemInfo.graphicsDeviceType);
            CreateUI();
            UpdateCamera(true);
        }
        public void BeginJourney()
        {
            Started=true; Finished=false; arrivalTime=0;
            startPanel.SetActive(false); endPanel.SetActive(false);
        }
        public void RestartJourney()
        {
            player.enabled=false; player.transform.position=spawn; player.enabled=true;
            visual.localRotation=Quaternion.identity;
            Collected=0; verticalSpeed=0; yaw=0; pitch=25;
            for(int i=0;i<picked.Length;i++) { picked[i]=false; postcards[i].gameObject.SetActive(true); }
            ResetInput(); BeginJourney(); UpdateCamera(true);
        }
        public bool TryDepart()
        {
            if(!Started || Finished || Collected!=postcards.Length || Vector3.Distance(player.transform.position,destination.position)>3) return false;
            Finished=true; endPanel.SetActive(true); ResetInput(); return true;
        }
        public void CheckPickups()
        {
            if(!Started || Finished) return;
            for(int i=0;i<postcards.Length;i++)
            {
                var offset=player.transform.position-postcards[i].position; offset.y=0;
                if(!picked[i] && offset.sqrMagnitude<1.8f*1.8f)
                { picked[i]=true; Collected++; postcards[i].gameObject.SetActive(false); }
            }
        }
        public void SimulateMovement(Vector2 input, bool jump, float dt)
        {
            if(!Started || Finished) return;
            Vector3 move=Quaternion.Euler(0,yaw,0)*new Vector3(input.x,0,input.y);
            move=Vector3.ClampMagnitude(move,1);
            if(player.isGrounded && verticalSpeed<0) verticalSpeed=-2;
            if(jump && player.isGrounded) verticalSpeed=6;
            verticalSpeed-=18*dt;
            player.Move((move*4.2f+Vector3.up*verticalSpeed)*dt);
            if(move.sqrMagnitude>.01f) visual.rotation=Quaternion.Slerp(visual.rotation,Quaternion.LookRotation(move),dt*14);
            if(player.transform.position.y < -5)
            { player.enabled=false; player.transform.position=spawn; player.enabled=true; verticalSpeed=0; }
        }
        void Update()
        {
            bool portrait=Screen.height>Screen.width;
            rotatePanel.SetActive(portrait);
            var safe=Screen.safeArea;
            safeRoot.anchorMin=new Vector2(safe.xMin/Screen.width,safe.yMin/Screen.height);
            safeRoot.anchorMax=new Vector2(safe.xMax/Screen.width,safe.yMax/Screen.height);
            if(!Started || Finished || portrait || !focused) { ResetInput(); return; }
            float dt=Mathf.Min(Time.deltaTime,.05f);
            arrivalTime+=dt;
            train.position=trainHome+Vector3.back*Mathf.Lerp(24,0,Mathf.SmoothStep(0,1,Mathf.Clamp01(arrivalTime/3)));
            var move=movePad.Value;
            var keyboard=Keyboard.current;
            if(keyboard!=null)
            {
                move+=new Vector2((keyboard.dKey.isPressed?1:0)-(keyboard.aKey.isPressed?1:0),
                                  (keyboard.wKey.isPressed?1:0)-(keyboard.sKey.isPressed?1:0));
                jumpRequested|=keyboard.spaceKey.wasPressedThisFrame;
                interactRequested|=keyboard.eKey.wasPressedThisFrame;
            }
            var look=lookPad.ConsumeLook();
            yaw+=look.x*.14f; pitch=Mathf.Clamp(pitch-look.y*.10f,12,60);
            SimulateMovement(move,jumpRequested,dt);
            jumpRequested=false;
            CheckPickups();
            if(interactRequested) TryDepart();
            interactRequested=false;
            for(int i=0;i<postcards.Length;i++) if(!picked[i]) postcards[i].Rotate(0,45*dt,0,Space.World);
            counter.text=Collected+" / "+postcards.Length+"   POSTCARDS";
            objective.text=Collected<postcards.Length ? "A LITTLE WALK BEFORE THE FAIR\nFind the three golden postcards." : "YOUR FIRST STOP IS COMPLETE\nWalk to the turquoise departure arch.";
            bool near=Vector3.Distance(player.transform.position,destination.position)<3;
            prompt.text=near ? (Collected==postcards.Length ? "Tap GO or press E to finish this visit" : "Find all three postcards before departing") : "Explore the platform  /  drag right side to look";
        }
        void LateUpdate() { if(gameCamera && player) UpdateCamera(false); }
        void UpdateCamera(bool snap)
        {
            var target=player.transform.position+Vector3.up*1.25f;
            var offset=Quaternion.Euler(pitch,yaw,0)*new Vector3(0,0,-6.5f);
            var desired=target+offset;
            if(Physics.SphereCast(target,.2f,offset.normalized,out var hit,offset.magnitude,1<<0,QueryTriggerInteraction.Ignore))
                desired=target+offset.normalized*Mathf.Max(.5f,hit.distance-.15f);
            gameCamera.transform.position=snap?desired:Vector3.Lerp(gameCamera.transform.position,desired,1-Mathf.Exp(-12*Time.unscaledDeltaTime));
            gameCamera.transform.LookAt(target);
        }
        void OnApplicationFocus(bool value) { focused=value; if(!value) ResetInput(); }
        void OnApplicationPause(bool value) { focused=!value; if(value) ResetInput(); }
        void ResetInput() { if(movePad)movePad.ResetInput(); if(lookPad)lookPad.ResetInput(); jumpRequested=false; interactRequested=false; }

        RectTransform Rect(string name, Transform parent, Vector2 min, Vector2 max, Vector2 size, Vector2 pos)
        {
            var rect=new GameObject(name,typeof(RectTransform)).GetComponent<RectTransform>();
            rect.SetParent(parent,false); rect.anchorMin=min; rect.anchorMax=max; rect.sizeDelta=size; rect.anchoredPosition=pos;
            return rect;
        }
        Image Panel(string name, Transform parent, Vector2 min, Vector2 max, Vector2 size, Vector2 pos, Color color)
        { var rt=Rect(name,parent,min,max,size,pos); var img=rt.gameObject.AddComponent<Image>(); img.color=color; return img; }
        Text Label(string name,string value,Transform parent,Vector2 min,Vector2 max,Vector2 size,Vector2 pos,int fontSize,TextAnchor align)
        {
            var rt=Rect(name,parent,min,max,size,pos); var t=rt.gameObject.AddComponent<Text>();
            t.text=value; t.font=font; t.fontSize=fontSize; t.alignment=align; t.color=new Color(.97f,.94f,.83f); t.raycastTarget=false;
            return t;
        }
        Button Button(string title,Transform parent,Vector2 anchor,Vector2 size,Vector2 pos,UnityEngine.Events.UnityAction action)
        {
            var img=Panel(title,parent,anchor,anchor,size,pos,new Color(.09f,.37f,.36f,.96f));
            var button=img.gameObject.AddComponent<Button>(); button.targetGraphic=img; button.onClick.AddListener(action);
            Label(title+" text",title,img.transform,Vector2.zero,Vector2.one,Vector2.zero,Vector2.zero,20,TextAnchor.MiddleCenter);
            return button;
        }
        void CreateUI()
        {
            var canvas=new GameObject("HNP Interface",typeof(Canvas),typeof(CanvasScaler),typeof(GraphicRaycaster));
            canvas.GetComponent<Canvas>().renderMode=RenderMode.ScreenSpaceOverlay;
            var scaler=canvas.GetComponent<CanvasScaler>(); scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution=new Vector2(1280,720); scaler.matchWidthOrHeight=.5f;
            var events=new GameObject("HNP EventSystem",typeof(EventSystem),typeof(InputSystemUIInputModule));
            events.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
            safeRoot=Rect("Safe area",canvas.transform,Vector2.zero,Vector2.one,Vector2.zero,Vector2.zero);
            var look=Panel("Look pad",safeRoot,new Vector2(.40f,0),Vector2.one,Vector2.zero,Vector2.zero,new Color(0,0,0,0));
            lookPad=look.gameObject.AddComponent<HnpTouchPad>(); lookPad.cameraPad=true;
            var heading=Panel("Heading",safeRoot,new Vector2(0,1),new Vector2(0,1),new Vector2(360,102),new Vector2(200,-70),new Color(.035f,.13f,.14f,.88f));
            Label("Title","HELLO\nNAKORNPATHOM",heading.transform,Vector2.zero,Vector2.one,new Vector2(-28,-12),Vector2.zero,26,TextAnchor.MiddleLeft);
            Label("Edition","01  /  THE STATION",safeRoot,new Vector2(0,1),new Vector2(0,1),new Vector2(360,35),new Vector2(200,-142),16,TextAnchor.MiddleLeft);
            var tasks=Panel("Journey",safeRoot,Vector2.one,Vector2.one,new Vector2(380,112),new Vector2(-210,-75),new Color(.035f,.13f,.14f,.88f));
            objective=Label("Objective","Find the three golden postcards.",tasks.transform,Vector2.zero,Vector2.one,new Vector2(-28,-30),new Vector2(0,12),19,TextAnchor.MiddleLeft);
            counter=Label("Counter","0 / 3   POSTCARDS",tasks.transform,new Vector2(0,0),new Vector2(1,0),new Vector2(-28,30),new Vector2(0,20),16,TextAnchor.MiddleLeft);
            var pad=Panel("Move pad",safeRoot,Vector2.zero,Vector2.zero,new Vector2(144,144),new Vector2(110,112),new Color(.055f,.22f,.23f,.7f));
            movePad=pad.gameObject.AddComponent<HnpTouchPad>();
            movePad.knob=Panel("Knob",pad.transform,new Vector2(.5f,.5f),new Vector2(.5f,.5f),new Vector2(54,54),Vector2.zero,new Color(.93f,.78f,.46f,.9f)).rectTransform;
            movePad.knob.GetComponent<Image>().raycastTarget=false;
            Label("Move help","MOVE / WASD",safeRoot,Vector2.zero,Vector2.zero,new Vector2(190,28),new Vector2(110,24),15,TextAnchor.MiddleCenter);
            Button("JUMP",safeRoot,new Vector2(1,0),new Vector2(106,80),new Vector2(-78,88),()=>jumpRequested=true);
            Button("GO / E",safeRoot,new Vector2(1,0),new Vector2(106,80),new Vector2(-198,88),()=>interactRequested=true);
            prompt=Label("Prompt","",safeRoot,new Vector2(.5f,0),new Vector2(.5f,0),new Vector2(610,36),new Vector2(0,38),18,TextAnchor.MiddleCenter);
            startPanel=Modal("Welcome","A SMALL JOURNEY, A FAMILIAR PLACE","Welcome to Nakornpathom\n\nTake a stroll through the station.\nCollect 3 golden postcards, then visit the departure arch.\n\nWASD to walk / Space to jump / Drag to look\nTouch controls are available on screen.","START EXPLORING",BeginJourney,canvas.transform);
            endPanel=Modal("Complete","YOUR JOURNEY HAS JUST BEGUN","Station visit complete\n\nNext stop: the bridge and Phra Pathom Chedi.\n\nThis is the first playable station prototype.","EXPLORE AGAIN",RestartJourney,canvas.transform); endPanel.SetActive(false);
            rotatePanel=Modal("Rotate","PLEASE ROTATE YOUR PHONE","This journey is designed for landscape.\nTurn your phone sideways to continue.",null,null,canvas.transform); rotatePanel.SetActive(false);
        }
        GameObject Modal(string name,string title,string body,string button,UnityEngine.Events.UnityAction action,Transform parent)
        {
            var panel=Panel(name,parent,Vector2.zero,Vector2.one,Vector2.zero,Vector2.zero,new Color(.025f,.10f,.11f,.94f));
            Label("Eyebrow","HELLO NAKORNPATHOM  /  STATION PROTOTYPE",panel.transform,new Vector2(.5f,.5f),new Vector2(.5f,.5f),new Vector2(850,40),new Vector2(0,205),17,TextAnchor.MiddleCenter);
            Label("Title",title,panel.transform,new Vector2(.5f,.5f),new Vector2(.5f,.5f),new Vector2(1000,70),new Vector2(0,140),32,TextAnchor.MiddleCenter);
            Label("Body",body,panel.transform,new Vector2(.5f,.5f),new Vector2(.5f,.5f),new Vector2(850,225),new Vector2(0,-10),22,TextAnchor.MiddleCenter);
            if(button!=null) Button(button,panel.transform,new Vector2(.5f,.5f),new Vector2(300,65),new Vector2(0,-195),action);
            return panel.gameObject;
        }
    }
}
