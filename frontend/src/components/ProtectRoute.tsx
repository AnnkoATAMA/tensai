import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./AuthContext";

const ProtectRoute = () => {
    const { isAuthenticated } = useContext(AuthContext);
    const location = useLocation();

    // 未ログインの場合はログインページへ遷移し、元のページを `state` に保存
    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ redirectPath: location.pathname }} />;
    }

    return <Outlet />;
};

export default ProtectRoute;
