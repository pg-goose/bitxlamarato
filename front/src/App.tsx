import React from 'react';
import FloatingCard from './FloatingCard'; // Import the new component
import breathingImage from './assets/woman-breathing-fresh-air-in-the-mountain-in-winter.webp';

const App: React.FC = () => {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-black via-black/90 to-blue-950">
      <FloatingCard
        imageSrc={breathingImage}
        title="Welcome to My Cool Screen"
        description="This is a demonstration of a beautifully styled React application. Resize the window to see how the layout adapts!"
      />
    </div>
  );
};

export default App;
