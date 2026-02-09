import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { motion } from "framer-motion";

const Header = () => {
  const { theme, setTheme } = useTheme();

  return (
    <>
      <style>{`
        .nav-link:hover .nav-underline {
          width: 100%;
        }
      `}</style>
      
      <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/10 dark:bg-black/10 backdrop-blur-xl border-b border-white/20 dark:border-white/10 rounded-b-3xl shadow-lg"
    >
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.h1 
            className="font-hero text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <a href="/">The Route Cause</a>
          </motion.h1>

          {/* Navigation - Centrally placed */}
          <div className="absolute left-1/2 transform -translate-x-1/2">
            <nav className="flex items-center gap-8">
              <a 
                href="/dashboard"
                className="relative font-body font-medium text-gray-900 dark:text-gray-300 hover:text-blue-600 dark:hover:text-white transition-colors duration-300 text-lg nav-link"
              >
                Dashboard
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300 group-hover:w-full nav-underline"></span>
              </a>
              
              <a 
                href="/performance"
                className="relative font-body font-medium text-gray-900 dark:text-gray-300 hover:text-blue-600 dark:hover:text-white transition-colors duration-300 text-lg nav-link"
              >
                Performance Metrics
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300 group-hover:w-full nav-underline"></span>
              </a>
              
              <a 
                href="/emergency"
                className="relative font-body font-medium text-gray-900 dark:text-gray-300 hover:text-red-600 dark:hover:text-white transition-colors duration-300 text-lg nav-link"
              >
                Emergency Mode
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-300 group-hover:w-full nav-underline"></span>
              </a>
            </nav>
          </div>

          {/* Theme Toggle - Enhanced glass effect */}
          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="rounded-full w-12 h-12 bg-white/20 dark:bg-black/20 backdrop-blur-md border border-white/30 dark:border-white/10 hover:bg-white/30 dark:hover:bg-black/30 hover:border-white/40 dark:hover:border-white/20 transition-all duration-300 shadow-lg"
            >
              <Sun className="h-5 w-5 rotate-0 scale-100 transition-all duration-300 dark:-rotate-90 dark:scale-0 text-amber-500" />
              <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all duration-300 dark:rotate-0 dark:scale-100 text-blue-400" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </motion.div>
        </div>
      </div>
      
      {/* Subtle glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 rounded-b-3xl pointer-events-none"></div>
    </motion.header>
    </>
  );
};

export default Header;