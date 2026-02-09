"use client";
import React, { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const TrafficLanding: React.FC = () => {
  const carRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    const car = carRef.current;

    if (!car) return;

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: ".scroll-section",
        start: "top top",
        end: "bottom bottom",
        scrub: 1,
      },
    });

    tl.to(car, { x: "120vw", duration: 1 })
      .addPause("+=0") // Stop at checkpoint 1
      .to(car, { x: "80vw", duration: 1 })
      .addPause("+=0") // Stop at checkpoint 2
      .to(car, { x: "40vw", duration: 1 })
      .addPause("+=0") // Stop at checkpoint 3
      .to(car, { x: "0vw", duration: 1 }); // Exit to footer

    return () => {
      tl.kill();
    };
  }, []);

  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <img src="/hero-bg.png" alt="Hero" className="absolute inset-0 w-full h-full object-cover"/>
        {/* Black Mask */}
        <div className="absolute inset-0 bg-black/80" />
        <div className="absolute inset-0 bg-violet/80 mix-blend-multiply" />
        {/* Red Glows */}
        <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-red-500/40 to-transparent blur-2xl" />
        <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-red-500/40 to-transparent blur-2xl" />

        <h1 className="relative text-white text-6xl font-bold text-center drop-shadow-lg">
          Smarter Traffic 🚦
        </h1>
      </section>

      {/* Scroll Section */}
      <section className="scroll-section relative h-[300vh]">
        <div className="sticky top-1/3 space-y-32 flex flex-col items-center">
          <div className="bg-white/90 p-6 rounded-2xl shadow-xl w-96 text-center">
            <h2 className="font-bold text-xl">Wasted Time ⏳</h2>
            <p>Traffic jams cost billions of hours every year.</p>
          </div>
          <div className="bg-white/90 p-6 rounded-2xl shadow-xl w-96 text-center">
            <h2 className="font-bold text-xl">Pollution 🌍</h2>
            <p>Idling vehicles pump harmful CO₂ into the air.</p>
          </div>
          <div className="bg-white/90 p-6 rounded-2xl shadow-xl w-96 text-center">
            <h2 className="font-bold text-xl">Emergency Vehicles 🚑</h2>
            <p>Delays cost lives in critical situations.</p>
          </div>
        </div>

        {/* Car */}
        <img
          ref={carRef}
          src="/car.png"
          alt="Car"
          className="fixed bottom-10 w-60 z-50"
        />
      </section>

      {/* Footer */}
      <footer className="h-screen bg-black text-white flex items-center justify-center">
        <p className="text-lg">© 2025 TrafficX — Smarter Roads Ahead</p>
      </footer>
    </div>
  );
};

export default TrafficLanding;
