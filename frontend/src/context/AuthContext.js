
import React, { createContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // In a real app, verify token or fetch user me
            setUser({ email: 'user@example.com' }); // Placeholder or decode JWT
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const response = await apiLogin(email, password);
        localStorage.setItem('token', response.data.access_token);
        setUser({ email });
    };

    const register = async (email, password) => {
        await apiRegister(email, password);
        // Auto login after register? or just redirect. 
        // Let's just return true
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
