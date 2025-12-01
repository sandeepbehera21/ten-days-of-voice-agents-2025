'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from '@/components/app/session-provider';
import { useRoomContext } from '@livekit/components-react';
import { motion, AnimatePresence } from 'motion/react';
import { RoomEvent } from 'livekit-client';
import { useChatMessages } from '@/hooks/useChatMessages';
import { ChatTranscript } from '@/components/app/chat-transcript';

export function ImprovGame() {
    const { startSession, endSession, isSessionActive } = useSession();
    const room = useRoomContext();
    const [playerName, setPlayerName] = useState('');
    const [gameState, setGameState] = useState<'intro' | 'playing' | 'finished'>('intro');
    const [agentState, setAgentState] = useState<'listening' | 'speaking' | 'thinking'>('listening');
    const messages = useChatMessages();

    // Monitor room state
    useEffect(() => {
        if (isSessionActive) {
            setGameState('playing');
        } else {
            setGameState('intro');
        }
    }, [isSessionActive]);

    // Monitor agent audio to determine state (simple heuristic)
    useEffect(() => {
        if (!room) return;

        const onActiveSpeakersChanged = (speakers: any[]) => {
            // If agent is speaking (remote source)
            const agentSpeaking = speakers.some(s => !s.isLocal);
            if (agentSpeaking) {
                setAgentState('speaking');
            } else {
                setAgentState('listening');
            }
        };

        room.on(RoomEvent.ActiveSpeakersChanged, onActiveSpeakersChanged);
        return () => {
            room.off(RoomEvent.ActiveSpeakersChanged, onActiveSpeakersChanged);
        };
    }, [room]);

    const handleStart = () => {
        if (playerName.trim()) {
            startSession();
        }
    };

    const handleStop = () => {
        endSession();
        setGameState('finished');
    };

    return (
        <div className="relative w-full h-full flex flex-col items-center justify-center overflow-hidden p-4">
            {/* Background Ambience */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-slate-900 to-black z-0" />
            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20 z-0" />

            {/* Content */}
            <div className="relative z-10 w-full max-w-4xl h-full flex flex-col">
                <AnimatePresence mode="wait">
                    {gameState === 'intro' && (
                        <motion.div
                            key="intro"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="flex flex-col items-center gap-6 text-center m-auto"
                        >
                            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-violet-500 drop-shadow-lg">
                                IMPROV BATTLE
                            </h1>
                            <p className="text-slate-300 text-lg">
                                Enter the arena. Face the AI Host. <br /> Prove your wit.
                            </p>

                            <div className="w-full max-w-md space-y-4">
                                <input
                                    suppressHydrationWarning
                                    type="text"
                                    placeholder="Enter your Stage Name"
                                    value={playerName}
                                    onChange={(e) => setPlayerName(e.target.value)}
                                    className="w-full px-6 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-pink-500 backdrop-blur-md transition-all text-center text-xl font-bold"
                                />
                                <button
                                    onClick={handleStart}
                                    disabled={!playerName.trim()}
                                    className="w-full px-6 py-4 bg-gradient-to-r from-pink-600 to-violet-600 rounded-xl font-bold text-xl text-white shadow-lg shadow-pink-500/20 hover:shadow-pink-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    START SHOW
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {gameState === 'playing' && (
                        <motion.div
                            key="playing"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="flex flex-col h-full gap-4 w-full"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="px-4 py-1 rounded-full bg-white/10 border border-white/20 text-sm font-medium text-pink-300 backdrop-blur-sm">
                                        ON AIR
                                    </div>
                                    <h2 className="text-2xl font-bold text-white">
                                        {playerName}
                                    </h2>
                                </div>
                                <button
                                    onClick={handleStop}
                                    className="px-6 py-2 rounded-full bg-red-500/20 border border-red-500/50 text-red-200 hover:bg-red-500/30 transition-colors"
                                >
                                    End Show
                                </button>
                            </div>

                            <div className="flex-1 flex gap-4 overflow-hidden">
                                {/* Visualizer Area */}
                                <div className="flex-1 flex flex-col items-center justify-center gap-4">
                                    <div className="relative w-64 h-64 flex items-center justify-center">
                                        <div className={`absolute inset-0 rounded-full bg-gradient-to-tr from-pink-500 to-violet-500 blur-3xl opacity-30 animate-pulse ${agentState === 'speaking' ? 'opacity-60 scale-110' : ''} transition-all duration-500`} />

                                        <div className="w-full h-32 flex items-center justify-center gap-1">
                                            <AgentVisualizer room={room} />
                                        </div>
                                    </div>

                                    <div className="text-center space-y-2">
                                        <p className="text-slate-400 text-sm uppercase tracking-widest">Host Status</p>
                                        <p className="text-2xl font-medium text-white">
                                            {agentState === 'speaking' ? 'Speaking...' : 'Listening...'}
                                        </p>
                                    </div>
                                </div>

                                {/* Chat Transcript */}
                                <div className="w-96 flex flex-col bg-black/30 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden">
                                    <div className="px-4 py-3 border-b border-white/10">
                                        <h3 className="text-white font-semibold">Conversation</h3>
                                    </div>
                                    <div className="flex-1 overflow-hidden">
                                        <ChatTranscript messages={messages} />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {gameState === 'finished' && (
                        <motion.div
                            key="finished"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center space-y-6 m-auto"
                        >
                            <h2 className="text-4xl font-bold text-white">Show's Over!</h2>
                            <p className="text-slate-300">Thanks for playing, {playerName}.</p>
                            <button
                                onClick={() => setGameState('intro')}
                                className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
                            >
                                Play Again
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

function AgentVisualizer({ room }: { room: any }) {
    return (
        <div className="flex items-center justify-center gap-1 h-16">
            {[...Array(5)].map((_, i) => (
                <motion.div
                    key={i}
                    className="w-3 bg-white rounded-full"
                    animate={{
                        height: [10, 40, 10],
                        opacity: [0.5, 1, 0.5]
                    }}
                    transition={{
                        duration: 0.5 + Math.random() * 0.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: i * 0.1
                    }}
                />
            ))}
        </div>
    )
}
