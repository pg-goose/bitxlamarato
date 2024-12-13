import React from 'react';

interface FloatingCardProps {
    imageSrc: string;
    title: string;
    description: string;
}

const FloatingCard: React.FC<FloatingCardProps> = ({ imageSrc, title, description }) => {
    return (
        <div className="flex flex-wrap items-center justify-center w-4/5 h-3/5 max-w-screen-lg">
            {/* Floating Image */}
            <div className="flex justify-center w-2/5 max-w-sm md:w-1/2 mr-4">
                <img
                    src={imageSrc}
                    alt={title}
                    className="h-auto max-h-48 md:max-h-64 rounded-lg shadow-[0_10px_30px_rgba(0,0,0,0.8)]"
                />
            </div>
            {/* Text */}
            <div className="flex flex-col items-center justify-center w-3/5 md:w-2/5 text-left space-y-4">
                <h1 className="text-3xl font-bold text-white md:text-4xl">
                    {title}
                </h1>
                <p className="text-white text-lg md:text-xl">
                    {description}
                </p>
            </div>
        </div>
    );
};

export default FloatingCard;
