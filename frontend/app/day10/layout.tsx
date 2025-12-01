import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Day 10: Improv Battle",
  description: "Voice Improv Battle with Murf Falcon",
};

export default function Day10Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-purple-500 selection:text-white">
      {children}
    </div>
  );
}
