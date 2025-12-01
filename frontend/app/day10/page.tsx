'use client';

import { SessionProvider } from '@/components/app/session-provider';
import { ImprovGame } from '@/components/day10/ImprovGame';
import { AppConfig } from '@/app-config';

const day10Config: AppConfig = {
    pageTitle: 'Day 10: Improv Battle',
    pageDescription: 'Voice Improv Battle with Murf Falcon',
    companyName: 'Murf AI Challenge',
    supportsChatInput: false,
    supportsVideoInput: false,
    supportsScreenShare: false,
    isPreConnectBufferEnabled: false,
    logo: '/lk-logo.svg', // Placeholder
    startButtonText: 'Start Improv',
    accent: '#ec4899', // Pink-500
    accentDark: '#ec4899',
};

export default function Day10Page() {
    return (
        <SessionProvider appConfig={day10Config}>
            <ImprovGame />
        </SessionProvider>
    );
}
