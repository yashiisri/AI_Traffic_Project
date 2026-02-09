import React, { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

interface CardData {
  id: number;
  title: string;
  imageSrc: string;
  description: string;
}

const Problems: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cardsContainerRef = useRef<HTMLDivElement>(null);
  const carRef = useRef<HTMLImageElement>(null);
  const [isInView, setIsInView] = useState(false);

  // Sample card data - you can replace this with your actual data
  const cardData: CardData[] = [
    {
      id: 1,
      title: "Traffic Congestion Crisis",
      imageSrc: "/problem1.png",
      description: "Urban intersections waste billions of hours annually due to inefficient fixed-timer systems that can't adapt to real traffic patterns."
    },
    {
      id: 2,
      title: "Emergency Response Delays", 
      imageSrc: "/problem2.png",
      description: "Critical emergency vehicles are trapped in traffic, costing lives because traditional lights can't provide instant priority routing."
    },
    {
      id: 3,
      title: "Environmental Harm",
      imageSrc: "/problem3.png", 
      description: "Idling cars in traffic burn excess fuel, spewing harmful pollutants that degrade air quality and contribute to climate change."
    }
  ];

  useEffect(() => {
    const container = containerRef.current;
    const cardsContainer = cardsContainerRef.current;
    const car = carRef.current;

    if (!container || !cardsContainer || !car) return;

    // Set initial states
    gsap.set(car, { 
      x: '-120%',
      opacity: 0,
      scale: 0.8
    });
    gsap.set('.problem-card', { 
      x: '60vw', // Start off-screen right
      opacity: 0,
      scale: 1
    });

    // Create the main scroll trigger for the horizontal scroll
    const horizontalScroll = gsap.timeline({
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: '+=400%',
        pin: true,
        scrub: 1,
        anticipatePin: 1,
        onEnter: () => setIsInView(true),
        onLeave: () => setIsInView(false),
        onEnterBack: () => setIsInView(true),
        onLeaveBack: () => setIsInView(false),
      }
    });

    // Car enters with first card (0% - 20% of timeline)
    horizontalScroll.to(car, {
      opacity: 1,
      scale: 1,
      x: '20vw', // Car enters and stops at first position
      duration: 0.2,
      ease: 'power2.out'
    }, 0);

    // First card appears with car entrance
    horizontalScroll.to('.problem-card-0', {
      x: 0,
      opacity: 1,
      duration: 0.2,
      ease: 'power1.out'
    }, 0);

    // Car moves to second position (20% - 50% of timeline)
    horizontalScroll.to(car, {
      x: '50vw',
      duration: 0.3,
      ease: 'power1.inOut'
    }, 0.2);

    // Second card appears as car reaches middle
    horizontalScroll.to('.problem-card-1', {
      x: 0,
      opacity: 1,
      duration: 0.25,
      ease: 'power1.out'
    }, 0.3);

    // Third card appears early (by 65% of timeline instead of later)
    horizontalScroll.to('.problem-card-2', {
      x: 0,
      opacity: 1,
      duration: 0.2,
      ease: 'power1.out'
    }, 0.6);

    // Car moves to final position and exits (85% - 100% of timeline)
    horizontalScroll.to(car, {
      x: '110vw', // Car exits screen
      duration: 0.15,
      ease: 'power2.in'
    }, 0.85);

    // Cleanup function
    return () => {
      ScrollTrigger.getAll().forEach(trigger => {
        if (trigger.trigger === container) {
          trigger.kill();
        }
      });
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className="relative w-full h-screen overflow-hidden bg-background"
    >
      {/* Cards Container */}
      <div 
        ref={cardsContainerRef}
        className="absolute inset-0 flex items-center justify-center gap-6 px-6 pt-40 pb-20"
      >
        {cardData.map((card, index) => (
          <div
            key={card.id}
            className={`problem-card problem-card-${index} bg-card rounded-2xl shadow-xl border border-border p-6 max-w-xs w-full transform hover:shadow-glow transition-all duration-300`}
            style={{ zIndex: 10 }}
          >
            {/* Card Header */}
            <div className="mb-4">
              <h3 className="font-hero text-xl font-bold text-foreground mb-2">
                {card.title}
              </h3>
            </div>

            {/* Card Image Placeholder */}
            <div className="mb-4 rounded-xl h-40 overflow-hidden border border-border">
              <img 
                src={card.imageSrc} 
                alt={card.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  // Fallback if image fails to load
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const fallback = document.createElement('div');
                  fallback.className = 'w-full h-full bg-muted flex items-center justify-center';
                  fallback.innerHTML = `
                    <div class="text-muted-foreground text-center">
                      <div class="w-16 h-16 bg-gradient-primary rounded-full mx-auto mb-3 flex items-center justify-center">
                        <div class="w-8 h-8 bg-primary-foreground rounded-full"></div>
                      </div>
                      <p class="font-body text-sm font-medium">Image not found</p>
                      <p class="font-body text-xs opacity-70">${card.imageSrc}</p>
                    </div>
                  `;
                  if (target.parentNode) {
                    target.parentNode.appendChild(fallback);
                  }
                }}
              />
            </div>

            {/* Card Description */}
            <div className="text-muted-foreground font-body leading-relaxed mb-4">
              <p>{card.description}</p>
            </div>

            {/* Additional content space */}
            
          </div>
        ))}
      </div>

      {/* Car Element */}
      <img
        ref={carRef}
        src="car.png"
        alt="Car"
        className="absolute bottom-8 h-20 w-auto object-contain z-[5] filter drop-shadow-lg"
        onError={(e) => {
          // Fallback if car.png is not available
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          const fallback = document.createElement('div');
          fallback.className = 'absolute bottom-8 h-16 w-28 bg-gradient-primary rounded-xl flex items-center justify-center text-primary-foreground text-sm font-hero font-bold shadow-glow';
          fallback.textContent = 'CAR';
          fallback.style.zIndex = '5';
          if (target.parentNode) {
            target.parentNode.insertBefore(fallback, target);
          }
        }}
      />

      {/* Section Title - matching your theme */}
      <div className="absolute top-20 left-1/2 transform -translate-x-1/2 text-center z-30">
        <h2 className="font-hero text-5xl md:text-7xl bg-gradient-primary bg-clip-text text-transparent">
          The Problems We Solve
        </h2>
      </div>
    </div>
  );
};

export default Problems;