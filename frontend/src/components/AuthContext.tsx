import { createContext, ReactNode, useState, useEffect } from "react";

interface AuthContextType {
    isAuthenticated: boolean | null;
    setIsAuthenticated: (auth: boolean | null) => void;
}

export const AuthContext = createContext<AuthContextType>({
    isAuthenticated: null,
    setIsAuthenticated: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(() => {
        return localStorage.getItem("isAuthenticated") === "true";
    });

    useEffect(() => {
        localStorage.setItem("isAuthenticated", String(isAuthenticated));
    }, [isAuthenticated]);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
};
