import React from 'react';

export const Table = ({ className, ...props }) => {
    return (
        <div className="w-full overflow-x-auto">
            <table
                className={`min-w-full divide-y divide-gray-200 ${className || ''}`}
                {...props}
            />
        </div>
    );
};

export const TableHeader = ({ className, ...props }) => {
    return (
        <thead
            className={`bg-gray-50 ${className || ''}`}
            {...props}
        />
    );
};

export const TableBody = ({ className, ...props }) => {
    return (
        <tbody
            className={`bg-white divide-y divide-gray-200 ${className || ''}`}
            {...props}
        />
    );
};

export const TableRow = ({ className, ...props }) => {
    return (
        <tr
            className={`hover:bg-gray-50 ${className || ''}`}
            {...props}
        />
    );
};

export const TableHead = ({ className, ...props }) => {
    return (
        <th
            className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${className || ''}`}
            {...props}
        />
    );
};

export const TableCell = ({ className, ...props }) => {
    return (
        <td
            className={`px-6 py-4 whitespace-nowrap text-sm text-gray-500 ${className || ''}`}
            {...props}
        />
    );
}; 