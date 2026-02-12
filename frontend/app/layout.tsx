import type { ReactNode } from "react";
import { Inter } from "next/font/google";
import { StoreProvider } from "./StoreProvider";
import "./styles/globals.css";
import Header from "./components/header";
import Footer from "./components/footer";
import AuthGuard from "./components/auth-guard";

const inter = Inter({ subsets: ["latin"] });

interface Props {
  readonly children: ReactNode;
}

export default function RootLayout({ children }: Props) {
  return (
    <StoreProvider>
      <html lang="en" className={inter.className}>
        <body>
          <AuthGuard>
            <Header />
            {children}
            <Footer />
          </AuthGuard>
        </body>
      </html>
    </StoreProvider>
  );
}
