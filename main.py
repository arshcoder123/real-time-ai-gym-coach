import streamlit as st
import time
import os
import pandas as pd
from dotenv import load_dotenv
from services.auth.login_wall import render_login_wall
from services.state.session_state import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css
from services.persistence.excercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.excercise_repository import get_user_exercises
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline,autoplay_audio

load_dotenv()
def main():
    st.set_page_config(
        page_icon="🏋️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered")

    load_css()

    init_db()

    if not render_login_wall():
        return

    initial_session_defaults()

    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY","")

            if not api_key and hasattr(st,"secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]

            groq_client = Groq(api_key=api_key)
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach,tts)
        except Exception:
            st.session_state.voice_pipeline = None

    workout_started = st.session_state.get("workout_started",False)

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🏋️</div>
                <div>
                    <div class="sidebar-brand-title">AI Coach</div>
                    <div class="sidebar-brand-subtitle">Real-time workout assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.username:
            st.caption(f"👤 {st.session_state.username}")

        st.divider()

        st.markdown(
            """
            <div class="sidebar-section-title">
                WORKOUT PLAN
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not workout_started:
            plan_exercise = st.selectbox("Exercise",options=EXERCISE_OPTIONS,key="plan_exercise")

            plan_sets = st.number_input("Sets",min_value=0,max_value=50,key="plan_sets",step=1)
            plan_reps = st.number_input("Reps Per set",min_value=0,max_value=50,key="plan_reps",step=1)

            st.markdown("")

            start_session_button = st.button("Start Workout",width="stretch",key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={}
                    )

                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_completed= 0
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")

            st.markdown(
                """
                <div class="workout-live-status">
                    <span class="live-dot">●</span>
                    WORKOUT IN PROGRESS
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")

            end_session_button = st.button("End Workout",key="end_session_button")

            if end_session_button:
                st.session_state.workout_started = False
                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.rerun()

        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("target_sets")


            st.subheader("Progress")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Reps", f"{total_reps}")
                st.metric("Sets", f"{sets_completed} / {target_sets}")

            with col2:
                st.metric("Current Set", f"{current_set_reps} / {reps_per_set}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Knee", f"{st.session_state.knee_angle}°")
                with col2:
                    st.metric("Back", f"{st.session_state.back_angle}°")
                st.metric("Depth", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Elbow", f"{st.session_state.elbow_angle}°")
                with col2:
                    st.metric("Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Elbow", f"{st.session_state.elbow_angle}°")
                with col2:
                    st.metric("Shoulder", st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Elbow", f"{st.session_state.elbow_angle}°")
                with col2:
                    st.metric("Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Front Knee", f"{st.session_state.front_knee_angle}°")
                with col2:
                    st.metric("Torso", f"{st.session_state.torso_angle}°")
                st.metric("Balance", st.session_state.balance_status)

    st.title("🏋️ AI Real-time GYM Coach")
    st.markdown("""#### Real-time pose detection with proactive AI voice coaching""")

    if st.session_state.get("audio_to_play"):
        autoplay_audio(st.session_state.audio_to_play)

    if st.session_state.get("coach_feedback"):
        st.markdown(
            f"""
            <div class="coach-card">
                <div class="coach-card-header">
                    <span class="coach-icon">🤖</span>
                    <span>AI Coach</span>
                </div>
                <div class="coach-message">
                    {st.session_state.coach_feedback}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not workout_started:
        st.markdown(
            """
            <div class="welcome-card">
                <div class="welcome-icon">🏋️</div>
                <h2>Ready to Train?</h2>
                <p>
                    Set your workout plan from the sidebar to start
                    real-time pose detection and AI coaching.
                </p>
                <div class="welcome-hint">
                    👈 Choose your exercise, sets and reps
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            """
            <div class="camera-header">
                <div>
                    <h3>📹 Live Workout Camera</h3>
                    <p>Real-time pose detection is active</p>
                </div>
                <div class="camera-status">
                    ● LIVE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302"]}
                ]
            },
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

    st.divider()

    st.markdown(
        """
        <div class="history-header">
            <div>
                <h3>📊 Workout History</h3>
                <p>Your completed workout sessions</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_id = st.session_state.get("user_id",0)

    if isinstance(user_id,int):
        history_rows = get_user_exercises(user_id)

        arr= [
            {
                "Exercise": row['exercise_name'],
                "Reps": row['reps'],
                "Sets": row['sets'],
                "Time (sec)": row['time'],
                "Date": row['created_at']
            }
            for row in history_rows
        ]

        df = pd.DataFrame(arr)

        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d %b %Y, %I:%M %p")
            agg_df = df.groupby(["Exercise","Date"]).agg(
                {
                    "Reps":"sum",
                    "Sets":"sum",
                    "Time (sec)":"sum",
                }
            ).reset_index()
            agg_df.insert(0, "No.", range(1, len(agg_df) + 1))
            st.table(agg_df,border="horizontal")

        else:
            st.info("No workout history found.")

if __name__=="__main__":
    main()