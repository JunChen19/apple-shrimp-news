/**
 * 首页 - 四大板块入口
 */
import Link from 'next/link';
import type { Article } from '../types';

const CATEGORIES = [
  {
    id: 'llm',
    name: '🤖 大模型动态',
    description: 'GPT、Claude、Llama 等重大更新',
    color: 'from-blue-500 to-blue-600',
  },
  {
    id: 'industry',
    name: '📰 AI 行业资讯',
    description: '融资、并购、创业、产品发布',
    color: 'from-green-500 to-green-600',
  },
  {
    id: 'politics',
    name: '🌍 国际政治',
    description: 'AI、科技政策相关的国际动态',
    color: 'from-purple-500 to-purple-600',
  },
  {
    id: 'finance',
    name: '💰 金融板块',
    description: '科技股、AI 概念股、融资信息',
    color: 'from-orange-500 to-orange-600',
  },
];

export default async function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">🦐 苹果虾资讯</h1>
              <p className="text-gray-600 mt-1">AI 资讯聚合平台 - 每日更新</p>
            </div>
            <div className="flex items-center space-x-4">
              <input
                type="text"
                placeholder="搜索资讯..."
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="btn-primary">搜索</button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* 板块卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {CATEGORIES.map((category) => (
            <Link
              key={category.id}
              href={`/news/${category.id}`}
              className={`block card bg-gradient-to-br ${category.color} text-white`}
            >
              <h2 className="text-2xl font-bold mb-2">{category.name}</h2>
              <p className="text-white/90">{category.description}</p>
              <div className="mt-4 flex items-center text-white/80">
                <span>查看详情</span>
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>

        {/* 最新文章 */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">最新文章</h2>
            <Link href="/news/all" className="text-blue-600 hover:text-blue-700">
              查看全部 →
            </Link>
          </div>
          <LatestArticles />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>🦐 苹果虾资讯 © 2026</p>
            <p className="mt-2 text-sm">数据来源：Tavily API | 每日早晨 7:00 自动更新</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/**
 * 最新文章列表组件
 */
async function LatestArticles() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  let articles = [];
  try {
    const res = await fetch(`${apiUrl}/api/articles?limit=8`, {
      cache: 'no-store',
      next: { revalidate: 300 }, // 5 分钟重新验证
    });
    if (res.ok) {
      articles = await res.json();
    }
  } catch (error) {
    console.error('获取文章失败:', error);
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>暂无文章，等待定时任务抓取...</p>
        <p className="text-sm mt-2">定时任务时间：每天早晨 7:00</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {articles.map((article: Article) => (
        <article
          key={article.id}
          className="card hover:shadow-xl transition-shadow"
        >
          <div className="flex items-start justify-between mb-3">
            <span className={`text-xs px-2 py-1 rounded-full ${
              article.category === 'llm' ? 'bg-blue-100 text-blue-800' :
              article.category === 'industry' ? 'bg-green-100 text-green-800' :
              article.category === 'politics' ? 'bg-purple-100 text-purple-800' :
              'bg-orange-100 text-orange-800'
            }`}>
              {article.category === 'llm' ? '🤖 大模型' :
               article.category === 'industry' ? '📰 行业' :
               article.category === 'politics' ? '🌍 政治' :
               '💰 金融'}
            </span>
            <span className="text-xs text-gray-500">
              {article.source}
            </span>
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
            {article.title}
          </h3>
          
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {article.summary}
          </p>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">
              {article.published_at ? new Date(article.published_at).toLocaleDateString('zh-CN') : '未知时间'}
            </span>
            <Link
              href={`/article/${article.id}`}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              阅读全文 →
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}
