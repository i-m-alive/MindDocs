// src/components/ParticleBackground.js
import React from 'react';
import Particles from 'react-tsparticles';
import { loadFull } from 'tsparticles';

function ParticleBackground() {
  const particlesInit = async (main) => {
    await loadFull(main);
  };

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        fullScreen: { enable: true, zIndex: -1 },
        background: {
          color: {
            value: 'transparent',
          },
        },
        particles: {
          number: {
            value: 40,
            density: {
              enable: true,
              area: 1000,
            },
          },
          color: {
            value: '#915EFF',
          },
          links: {
            enable: true,
            distance: 150,
            color: '#915EFF',
            opacity: 0.4,
            width: 1,
          },
          move: {
            enable: true,
            speed: 1,
          },
          size: {
            value: 3,
          },
          opacity: {
            value: 0.5,
          },
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: 'repulse' },
            onClick: { enable: true, mode: 'push' },
          },
          modes: {
            repulse: { distance: 100 },
            push: { quantity: 4 },
          },
        },
      }}
    />
  );
}

export default ParticleBackground;
