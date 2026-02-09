import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

const HeroText = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const opacity = useTransform(scrollYProgress, [0, 0.7, 1], [1, 0.5, 0]);

  return (
    <div ref={containerRef} className="relative h-screen flex items-center justify-center">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0"
        style={{
          backgroundImage: "url('/hero-bg.png')",
        }}
      />
      
      {/* Black mask overlay with theme-responsive opacity */}
      <div className="absolute inset-0 bg-black opacity-25 dark:opacity-65 z-0" />
      
      <div className="absolute inset-0 z-0">
        {/* Left dark glow - enhanced */}
        <div 
          className="absolute left-0 top-0 h-full w-48 opacity-60"
          style={{
            background: `linear-gradient(to right, #020817, rgba(2, 8, 23, 0.4), rgba(2, 8, 23, 0.1), transparent)`
          }}
        />
        
        {/* Right dark glow - enhanced */}
        <div 
          className="absolute right-0 top-0 h-full w-48 opacity-60"
          style={{
            background: `linear-gradient(to left, #020817, rgba(2, 8, 23, 0.4), rgba(2, 8, 23, 0.1), transparent)`
          }}
        />
        
        {/* Additional inner glow for more depth */}
        <div 
          className="absolute left-0 top-0 h-full w-24 opacity-40"
          style={{
            background: `linear-gradient(to right, rgba(2, 8, 23, 0.3), rgba(2, 8, 23, 0.1), transparent)`
          }}
        />
        <div 
          className="absolute right-0 top-0 h-full w-24 opacity-40"
          style={{
            background: `linear-gradient(to left, rgba(2, 8, 23, 0.3), rgba(2, 8, 23, 0.1), transparent)`
          }}
        />
      </div>

      {/* Text content */}
      <motion.div
        style={{ y, opacity }}
        className="text-center z-10 px-6 relative"
      >
        <motion.h1
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
          className="font-hero text-6xl md:text-8xl lg:text-9xl mb-6 bg-gradient-hero bg-clip-text text-transparent leading-tight"
        >
          The Algorithm 
        </motion.h1>
        
        <motion.h2
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1, delay: 0.7, ease: "easeOut" }}
          className="font-hero text-6xl md:text-8xl lg:text-9xl mb-8 bg-gradient-hero bg-clip-text text-transparent leading-tight"
        >
          of the Open Road.
        </motion.h2>
      </motion.div>
    </div>
  );
};

export default HeroText;