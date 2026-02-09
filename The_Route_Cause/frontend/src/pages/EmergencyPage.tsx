"use client";
import Header from "@/components/Header"; 
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import {  useTrafficData } from "@/components/trafficdataprovider";
import Footer from "@/components/Footer"; 

type EmergencyTrendPoint = {
  time: string;
  delayed_vehicles: number;
  total_vehicles: number;
};

const EmergencyPage = () => {
  const { data, isConnected } = useTrafficData();

  // State to determine if we are in an "active" emergency session
  const [isEmergencyActive, setIsEmergencyActive] = useState(false);
  // State to hold the data for the currently displayed emergency (or the last one)
  const [displayData, setDisplayData] = useState<any>(null);
  // State for the chart's historical data
  const [emergencyHistory, setEmergencyHistory] = useState<EmergencyTrendPoint[]>([]);
  
  // Ref to track the ID or key of the current emergency to detect a new one
  const currentEmergencyId = useRef<number | null>(null);

  useEffect(() => {
    const backendEmergencyData = data?.emergency_mode;
    const isEmergencyCleared = data?.main_dashboard?.signal_state?.reason?.includes("Emergency cleared");

    // --- LOGIC TO START A NEW EMERGENCY SESSION ---
    if (backendEmergencyData) {
      // Use timestamp as a simple ID for the emergency event
      const newEmergencyId = data.timestamp;

      if (currentEmergencyId.current !== newEmergencyId) {
        // This is a brand new emergency, clear the old history
        setEmergencyHistory([]);
        currentEmergencyId.current = newEmergencyId;
      }
      
      setIsEmergencyActive(true);
      setDisplayData(backendEmergencyData);

      const now = new Date();
      const newTrendPoint: EmergencyTrendPoint = {
        time: `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`,
        delayed_vehicles: backendEmergencyData.delayed_vehicles,
        total_vehicles: backendEmergencyData.total_vehicles,
      };

      setEmergencyHistory((prev) => [...prev, newTrendPoint].slice(-30));
    
    // --- LOGIC TO END AN EMERGENCY SESSION ---
    } else if (isEmergencyActive && isEmergencyCleared) {
      // The emergency is officially over. Stop the pulsing animation.
      // The data will remain frozen on the last known state.
      setIsEmergencyActive(false);
      currentEmergencyId.current = null; // Reset for the next event
    }

  }, [data, isEmergencyActive]);

  const chartConfig = {
    delayed_vehicles: { label: "Delayed Vehicles", color: "hsl(var(--destructive))" },
    total_vehicles: { label: "Total Vehicles", color: "hsl(var(--primary))" },
  };

  if (!isConnected || !data) {
    return (
      <>
        <Header />
        <div className="flex h-screen items-center justify-center bg-background relative overflow-hidden">
          {/* Animated background grid */}
          <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:50px_50px]" />
          
          {/* Animated gradient orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/20 rounded-full blur-3xl animate-pulse delay-700" />
          
          <div className="text-center z-10 space-y-8">
            
            
            {/* Main heading with gradient */}
            <h1 className="font-hero text-3xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-800 bg-clip-text text-transparent">
              {isConnected ? "Initializing AI Traffic Analysis..." : "Connecting to Traffic System..."}
            </h1>
            
            {/* Animated loading bar */}
            <div className="w-64 h-2 bg-secondary rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-gradient-to-r from-red-500 to-red-800 animate-[loading_1.5s_ease-in-out_infinite]" />
            </div>
            
            {/* Status messages */}
            <div className="space-y-2 text-muted-foreground">
              <p className="flex items-center justify-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                Establishing connection to backend server
              </p>
              <p className="text-sm opacity-70">
                Ensure the backend server and AI agent are running
              </p>
            </div>
            
            {/* System status indicators */}
            
          </div>
        </div>
        <style>{`
          @keyframes loading {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(400%); }
          }
          .delay-700 { animation-delay: 700ms; }
        `}</style>
      </>
    );
  }
  
  // --- RENDER NORMAL OR EMERGENCY VIEW ---
  // If we have never seen an emergency, or cleared it, show Normal Operations
  if (!displayData) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="pt-24 pb-12">
          <div className="container mx-auto px-6 text-center">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-500/20 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/20 rounded-full blur-3xl animate-pulse delay-700" />
          
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <h1 className="font-hero text-4xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-800 bg-clip-text text-transparent">
                Normal Operations
              </h1>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                The emergency monitoring system is active. All traffic signals are currently operating under standard AI control.
              </p>
               <div className="mt-8 text-6xl">🚨</div>
            </motion.div>
          </div>
        </main>
      </div>
    );
  }

  // Render the emergency dashboard (it will be pulsing if active, static if finished)
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="pt-24 pb-12">
        <div className="container mx-auto px-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="mb-8">
            <h1 className="font-hero text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
              {isEmergencyActive ? "Emergency Mode" : "Last Emergency Event"}
            </h1>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }} className="mb-8">
            <Card className={`border-destructive/20 bg-destructive/5 ${isEmergencyActive ? 'animate-pulse' : ''}`}>
              <CardHeader>
                <CardTitle className="text-destructive flex items-center gap-2">
                  🚨 Emergency Override {isEmergencyActive ? 'Active' : 'Finished'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div><span className="font-medium">Priority Direction:</span> {displayData.priority_direction}</div>
                  <div><span className="font-medium">Signal State:</span> GREEN</div>
                  <div><span className="font-medium">Timer:</span> {data?.main_dashboard?.signal_state?.timer ?? 0}s</div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <div className="grid gap-8 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
              <Card>
                <CardHeader><CardTitle className="text-destructive">Delayed Vehicles Trend</CardTitle></CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={emergencyHistory}>
                        <XAxis dataKey="time" />
                        <YAxis domain={[0, 'dataMax + 10']}/>
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line type="monotone" dataKey="delayed_vehicles" stroke="var(--color-delayed_vehicles)" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }}>
              <Card>
                <CardHeader><CardTitle className="text-primary">Total Vehicles Trend</CardTitle></CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={emergencyHistory}>
                        <XAxis dataKey="time" />
                        <YAxis domain={[0, 'dataMax + 10']}/>
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line type="monotone" dataKey="total_vehicles" stroke="var(--color-total_vehicles)" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>
          
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.4 }} className="mt-8">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-lg">Current Delayed Vehicles</CardTitle></CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-destructive">{displayData.delayed_vehicles}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-lg">Current Total Vehicles</CardTitle></CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-primary">{displayData.total_vehicles}</div>
                </CardContent>
              </Card>
            </div>
          </motion.div>

        </div>
      </main>
      <Footer />
    </div>
  );
};

export default EmergencyPage;

