import React, { useState } from "react";
import Problems from "@/components/Problems";
import Header from "@/components/Header";
import HeroText from "@/components/HeroText";
import ScrollContent from "@/components/ScrollContent";
import Footer from "@/components/Footer";
import Between from "@/components/Between";

const Index = () => {
  const [isLoading, setIsLoading] = useState(true);
  return (
    <div className="relative">
      (
        <>
                    
          {/* Header */}
          <Header />
          {/* Main Content */}
          <main className="relative z-10">
            {/* Hero Section with 3D Background */}
            <HeroText />
            <Between />
            {/*Problems horizontal scroll*/}
            <Problems />
            {/* Scrollable Content */}
            <div className="bg-gradient-subtle">
              <ScrollContent />
            </div>

          </main>
          
          {/* Footer */}
          <Footer />
        </>
      )
    </div>
  );
};

export default Index;