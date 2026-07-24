"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function SplashScreen() {
  const router = useRouter();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [particles, setParticles] = useState<React.ReactNode[]>([]);
  const [isHidden, setIsHidden] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const delayBeforeDisintegration = 2000;
    const particleSize = 6;

    const timer = setTimeout(() => {
      if (!wrapperRef.current || !containerRef.current) return;
      
      const rect = wrapperRef.current.getBoundingClientRect();
      
      // Hide original content instantly
      setIsHidden(true);

      const cols = Math.floor(rect.width / particleSize);
      const rows = Math.floor(rect.height / particleSize);
      
      const newParticles = [];
      const pElements: { id: string, tx: number, ty: number, rot: number, scale: number }[] = [];

      for (let i = 0; i < cols; i += 2) {
        for (let j = 0; j < rows; j += 2) {
          if (Math.random() > 0.6) continue;

          const id = `p-${i}-${j}`;
          const opacity = 0.5 + Math.random() * 0.5;
          
          // Pre-calculate target transforms
          const angle = Math.random() * Math.PI * 2;
          const velocity = 50 + Math.random() * 300;
          const tx = Math.cos(angle) * velocity;
          const ty = Math.sin(angle) * velocity;
          const rot = (Math.random() - 0.5) * 720;
          const scale = Math.random() * 0.5;

          pElements.push({ id, tx, ty, rot, scale });

          newParticles.push(
            <div
              key={id}
              id={id}
              className="pixel-particle"
              style={{
                width: particleSize,
                height: particleSize,
                left: i * particleSize,
                top: j * particleSize,
                opacity: opacity,
              }}
            />
          );
        }
      }

      setParticles(
        <div 
          className="absolute pointer-events-none" 
          style={{ top: rect.top, left: rect.left, width: rect.width, height: rect.height }}
        >
          {newParticles}
        </div>
      );

      // Trigger animation next frame
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          pElements.forEach(p => {
            const el = document.getElementById(p.id);
            if (el) {
              el.style.transform = `translate(${p.tx}px, ${p.ty}px) rotate(${p.rot}deg) scale(${p.scale})`;
              el.style.opacity = '0';
            }
          });
        });
      });

      // Route away after animation
      setTimeout(() => {
        router.push("/role-select");
      }, 1600);

    }, delayBeforeDisintegration);

    return () => clearTimeout(timer);
  }, [router]);

  if (!mounted) return null; // Prevent hydration issues

  return (
    <div className="bg-[#131313] text-[#e2e2e2] overflow-hidden h-screen w-screen selection:bg-[#10b981] selection:text-[#131313] relative">
      {/* Scanlines overlay */}
      <div className="scanlines"></div>
      
      {/* Main Splash Container */}
      <main ref={containerRef} className="h-full w-full flex flex-col items-center justify-center relative z-10">
        
        {/* Content Wrapper (Target for disintegration) */}
        <div 
          ref={wrapperRef}
          className={`flex flex-col items-center justify-center relative glitch-load emerald-glow ${isHidden ? 'hide-content invisible' : ''}`}
        >
          {/* Logo */}
          <div className="w-32 h-32 mb-8 relative">
            <img 
              alt="DaeMon Square Grid Logo" 
              className="w-full h-full object-contain drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuD1JcJ1dpS1azV8hXhRQhL1fHy2LmJZd8p9g7l6vCLInzUiHEejmrNSv3HYKPPfTIUGiz0fYjDpnPkyGFYrATqHZwnY8Q9poGyDSf8k1tZcMvyoS2WXDRxVUnvQhzRsX2HI_aARcWlAkGdJmXF9GVY83Uu0nUFT2Envsks3fl4IupswOgKQjvGqZL27YrGF_EReVf3JSIyPB4MgM3jPBuhVo9Edrvhn5m9OTtA8pWnzcXF1Awc4Raw7bfkKtBiZQvgrPTntuOdd69cZ"
              crossOrigin="anonymous"
            />
            {/* Corner markers for technical aesthetic */}
            <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-[#4edea3]/40"></div>
            <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-[#4edea3]/40"></div>
            <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-[#4edea3]/40"></div>
            <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-[#4edea3]/40"></div>
          </div>
          
          {/* Title */}
          <h1 className="font-mono text-5xl md:text-6xl text-[#10b981] font-bold tracking-tighter uppercase">
            DaeMon
          </h1>
          
          {/* Subtitle */}
          <h2 className="font-sans text-sm md:text-base font-bold text-[#4edea3]/60 uppercase tracking-[0.4em] mt-3 ml-[0.4em] text-center border-t border-[#4edea3]/20 pt-3">
            Distributed Compute Grid
          </h2>
        </div>
      </main>

      {/* Disintegration Particles */}
      {particles}
    </div>
  );
}
