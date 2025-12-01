"""
Day 10: Improv Battle - Pure Voice Script (NO LLM)
Just STT + TTS + Pre-scripted responses
"""

import logging
import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, silero
from livekit import rtc

logger = logging.getLogger("day10-voice-only")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

# Pre-scripted responses
SCRIPT = [
    "Welcome to Improv Battle! I'm your host. What is your name, contestant?",
    "Fantastic! Great to have you here! Here's how this works: I'll give you a wild scenario, and you have to act it out with pure improvisation. Ready?",
    "Excellent! Here's your first scenario: You're a penguin trying to convince a polar bear that summer is better than winter. Go ahead, show me what you've got!",
    "Ha! That's hilarious! Okay, next scenario: You're a time traveler from the year 3000 explaining smartphones to someone from the 1800s. Action!",
    "Brilliant! Final round: You're a superhero whose only power is making really good sandwiches. Save the day!",
    "That was absolutely amazing! You've got serious improv skills! Thanks for playing Improv Battle! See you next time!"
]

class VoiceOnlyImprov:
    def __init__(self, room):
        self.room = room
        self.stt = deepgram.STT(model="nova-3")
        self.tts = deepgram.TTS(model="aura-asteria-en")
        self.script_index = 0
        self.audio_source = None
        self.audio_track = None
        
    async def speak(self, text: str):
        """Convert text to speech and play it"""
        logger.info(f"Speaking: {text}")
        
        try:
            # Generate audio
            stream = self.tts.synthesize(text)
            audio_data = []
            
            async for audio in stream:
                audio_data.append(audio.frame.data.tobytes())
            
            if audio_data:
                # Create audio source if not exists
                if not self.audio_source:
                    self.audio_source = rtc.AudioSource(24000, 1)
                    self.audio_track = rtc.LocalAudioTrack.create_audio_track("agent-voice", self.audio_source)
                    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
                    await self.room.local_participant.publish_track(self.audio_track, options)
                
                # Play audio
                for data in audio_data:
                    frame = rtc.AudioFrame(data, 24000, 1, len(data) // 2)
                    await self.audio_source.capture_frame(frame)
                    
        except Exception as e:
            logger.error(f"Error speaking: {e}")
    
    async def handle_user_speech(self, text: str):
        """Handle user input and respond with next script"""
        logger.info(f"User said: {text}")
        
        # Move to next response
        if self.script_index < len(SCRIPT):
            await self.speak(SCRIPT[self.script_index])
            self.script_index += 1
        else:
            await self.speak("Thanks for playing!")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        await ctx.connect()
        
        # Wait for participant
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")
        
        # Create voice handler
        game = VoiceOnlyImprov(ctx.room)
        
        # Say first greeting
        await game.speak(SCRIPT[0])
        game.script_index = 1
        
        # Listen for audio
        async def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                logger.info("Audio track subscribed")
                
                audio_stream = rtc.AudioStream(track)
                stt_stream = game.stt.stream()
                
                async def forward_audio():
                    async for event in audio_stream:
                        stt_stream.push_frame(event.frame)
                
                async def handle_transcription():
                    async for event in stt_stream:
                        if event.alternatives and event.is_final:
                            text = event.alternatives[0].text
                            if text.strip():
                                await game.handle_user_speech(text)
                
                await asyncio.gather(forward_audio(), handle_transcription())
        
        ctx.room.on("track_subscribed", on_track_subscribed)
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
