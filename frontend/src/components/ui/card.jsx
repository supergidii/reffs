import React from 'react';

export const Card = ({ className, ...props }) => {
    return (
        <div
            className={`bg-white rounded-lg shadow-md ${className || ''}`}
            {...props}
        />
    );
};

export const CardHeader = ({ className, ...props }) => {
    return (
        <div
            className={`px-6 py-4 border-b border-gray-200 ${className || ''}`}
            {...props}
        />
    );
};

export const CardTitle = ({ className, ...props }) => {
    return (
        <h3
            className={`text-lg font-semibold text-gray-900 ${className || ''}`}
            {...props}
        />
    );
};

export const CardContent = ({ className, ...props }) => {
    return (
        <div
            className={`px-6 py-4 ${className || ''}`}
            {...props}
        />
    );
}; 