using UnityEngine;

namespace HNP.GameCore
{
    public enum HnpLocomotionMode
    {
        Idle,
        Walk,
        Run
    }

    /// <summary>Device-neutral input produced by touch, keyboard, or an accessibility control.</summary>
    public struct HnpLocomotionInput
    {
        public Vector2 Move;
        public bool RunHeld;

        public HnpLocomotionInput(Vector2 move, bool runHeld)
        {
            Move = move;
            RunHeld = runHeld;
        }
    }

    public struct HnpLocomotionSettings
    {
        public float WalkSpeed;
        public float RunSpeed;
        public float DeadZone;

        public HnpLocomotionSettings(float walkSpeed, float runSpeed, float deadZone = 0.08f)
        {
            WalkSpeed = Mathf.Max(0f, walkSpeed);
            RunSpeed = Mathf.Max(WalkSpeed, runSpeed);
            DeadZone = Mathf.Clamp01(deadZone);
        }
    }

    public struct HnpLocomotionState
    {
        public Vector2 Direction;
        public float Speed;
        public HnpLocomotionMode Mode;

        public bool IsMoving => Mode != HnpLocomotionMode.Idle;
    }

    /// <summary>Resolves movement without reading Unity input or moving a scene object.</summary>
    public static class HnpLocomotionResolver
    {
        public static HnpLocomotionState Resolve(HnpLocomotionInput input, HnpLocomotionSettings settings, bool movementAllowed)
        {
            var direction = Vector2.ClampMagnitude(input.Move, 1f);
            if (!movementAllowed || direction.magnitude < settings.DeadZone)
            {
                return new HnpLocomotionState { Direction = Vector2.zero, Speed = 0f, Mode = HnpLocomotionMode.Idle };
            }

            var running = input.RunHeld;
            return new HnpLocomotionState
            {
                Direction = direction,
                Speed = running ? settings.RunSpeed : settings.WalkSpeed,
                Mode = running ? HnpLocomotionMode.Run : HnpLocomotionMode.Walk
            };
        }
    }
}
