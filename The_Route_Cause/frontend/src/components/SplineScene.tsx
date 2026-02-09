import Spline from '@splinetool/react-spline';
import { motion } from 'framer-motion';

const SplineScene = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 2, ease: "easeOut" }}
      className="fixed inset-0 z-0"
    >
      <Spline scene="" />
    </motion.div>
  );
};

export default SplineScene;
