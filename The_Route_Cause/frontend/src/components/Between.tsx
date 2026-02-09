import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const Between = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });
  
  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);

  return (
    <div ref={containerRef} className="relative py-20">
      <motion.div 
        style={{ y }}
        className="container mx-auto px-6"
      >
        {/* Section 1: Value Proposition */}
        <motion.section
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          viewport={{ once: true }}
          className="text-center"
        >
          <h2 className="font-hero text-5xl md:text-7xl mb-8 bg-gradient-primary bg-clip-text text-transparent">
            We've All Been There
          </h2>
          <p className="font-body text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed mb-12">
            You know the feeling: you're stuck at a red light at 3 a.m. on a completely empty road. Traditional traffic lights are like that friend who can't read the room—they just stick to the plan, no matter how ridiculous it becomes.
            <br /><br />
            Our system is the friend who actually looks around and says, "Hey, no one's here. Let's get you home already."
          </p>
          <Button className="bg-gradient-primary hover:shadow-glow text-primary-foreground px-8 py-4 text-lg font-medium group">
            <a href="/dashboard" className="flex items-center">
              Get Started
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </a>
          </Button>
        </motion.section>
      </motion.div>
    </div>
  );
};

export default Between;