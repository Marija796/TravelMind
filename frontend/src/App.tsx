import { Suspense, lazy, useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, useLocation, useParams, Navigate } from 'react-router-dom'
import { getDestination } from '@/services/destinations'
import { AnimatePresence } from 'framer-motion'
import { Toaster } from 'react-hot-toast'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { AuthProvider } from '@/context/AuthContext'
import { ThemeProvider } from '@/context/ThemeContext'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import ProtectedRoute from '@/components/common/ProtectedRoute'
import PageWrapper from '@/components/layout/PageWrapper'

const Home = lazy(() => import('@/pages/Home'))
const Explore = lazy(() => import('@/pages/Explore'))
const DestinationDetail = lazy(() => import('@/pages/DestinationDetail'))
const Recommendations = lazy(() => import('@/pages/Recommendations'))
const Profile = lazy(() => import('@/pages/Profile'))
const Wishlist = lazy(() => import('@/pages/Wishlist'))
const Visited = lazy(() => import('@/pages/Visited'))
const Login = lazy(() => import('@/pages/Login'))
const Register = lazy(() => import('@/pages/Register'))
const ForgotPassword = lazy(() => import('@/pages/ForgotPassword'))
const ResetPassword = lazy(() => import('@/pages/ResetPassword'))
const AppReviews = lazy(() => import('@/pages/AppReviews'))
const SimilarUsers = lazy(() => import('@/pages/SimilarUsers'))
const NotFound = lazy(() => import('@/pages/NotFound'))

function PageFallback() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

function LegacyDestinationRedirect() {
  const { id } = useParams<{ id: string }>()
  const [slug, setSlug] = useState<string | null>(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!id) { setNotFound(true); return }
    getDestination(Number(id))
      .then((d) => setSlug(d.slug))
      .catch(() => setNotFound(true))
  }, [id])

  if (notFound) return <Navigate to="/explore" replace />
  if (!slug) return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
  return <Navigate to={`/destination/${slug}`} replace />
}

function AnimatedRoutes() {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <Suspense fallback={<PageFallback />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<PageWrapper><Home /></PageWrapper>} />
          <Route path="/explore" element={<PageWrapper><Explore /></PageWrapper>} />
          <Route path="/destination/:slug" element={<PageWrapper><DestinationDetail /></PageWrapper>} />
          <Route path="/destinations/:id" element={<LegacyDestinationRedirect />} />
          <Route path="/login" element={<PageWrapper><Login /></PageWrapper>} />
          <Route path="/register" element={<PageWrapper><Register /></PageWrapper>} />
          <Route path="/forgot-password" element={<PageWrapper><ForgotPassword /></PageWrapper>} />
          <Route path="/reset-password" element={<PageWrapper><ResetPassword /></PageWrapper>} />
          <Route path="/recommendations" element={<PageWrapper><Recommendations /></PageWrapper>} />
          <Route path="/app-reviews" element={<PageWrapper><AppReviews /></PageWrapper>} />
          <Route
            path="/similar-users"
            element={
              <ProtectedRoute>
                <PageWrapper><SimilarUsers /></PageWrapper>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <PageWrapper><Profile /></PageWrapper>
              </ProtectedRoute>
            }
          />
          <Route
            path="/wishlist"
            element={
              <ProtectedRoute>
                <PageWrapper><Wishlist /></PageWrapper>
              </ProtectedRoute>
            }
          />
          <Route
            path="/visited"
            element={
              <ProtectedRoute>
                <PageWrapper><Visited /></PageWrapper>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<PageWrapper><NotFound /></PageWrapper>} />
        </Routes>
      </Suspense>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ''}>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
              <Navbar />
              <main className="flex-1">
                <AnimatedRoutes />
              </main>
              <Footer />
            </div>
            <Toaster
              position="top-right"
              toastOptions={{
                className: 'dark:bg-slate-800 dark:text-white',
                duration: 3000,
                style: { borderRadius: '12px', padding: '12px 16px' },
              }}
            />
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </GoogleOAuthProvider>
  )
}
