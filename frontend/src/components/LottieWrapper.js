import React from "react";
import Lottie from "lottie-react";

const LottieWrapper = ({ animationData, height = 300 }) => {
  return (
    <div className="d-flex justify-content-center my-4">
      <Lottie animationData={animationData} style={{ height }} loop />
    </div>
  );
};

export default LottieWrapper;
