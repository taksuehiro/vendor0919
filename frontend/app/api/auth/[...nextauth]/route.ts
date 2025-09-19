import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

const NEXTAUTH_URL = process.env.NEXTAUTH_URL
const NEXTAUTH_SECRET = process.env.NEXTAUTH_SECRET

const handler = NextAuth({
  secret: NEXTAUTH_SECRET,
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials) return null
        
        try {
          // FastAPIの認証APIを呼び出し
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              email: credentials.email, 
              password: credentials.password 
            })
          })
          
          if (!res.ok) return null  // 認証失敗時
          
          const user = await res.json()
          return {
            id: user.id.toString(),
            email: user.email,
            name: user.email
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        // NextAuthのJWTトークンをaccessTokenとして保存
        token.accessToken = token
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        // セッションにaccessTokenを追加
        session.accessToken = token.accessToken
      }
      return session
    }
  }
})

export { handler as GET, handler as POST }
