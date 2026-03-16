/**
 * 板块列表页
 */
import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Article } from '../../../types';

const CATEGORY_INFO: Record<string, { name: string; description: string; icon: string }> = {
  llm: { name: '🤖 大模型动态', description: 'GPT、Claude、Llama 等重大更新', icon: '🤖' },
  industry: { name: '📰 AI 行业资讯', description: '融资、并购、创业、产品发布', icon: '📰' },
  politics: { name: '🌍 国际政治', description: 'AI、科技政策相关的国际动态', icon: '🌍' },
  finance: { name: '💰 金融板块', description: '科技股、AI 概念股、融资信息', icon: '💰' },
  all: { name: '📚 全部资讯', description: '所有板块的最新资讯', icon: '📚' },
};

export default async function CategoryPage({ params }: { params: { category: string } }) {
  const category = params.category;
  const info = CATEGORY_INFO[category] || CATEGORY_INFO.all;

  if (!CATEGORY_INFO[category] && category !== 'all') {
    notFound();
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <Link href="/" className="text-blue-600 hover:text-blue-700">
            ← 返回首页
          </Link>
          <div className="mt-4">
            <h1 className="text-3xl font-bold text-gray-900">{info.name}</h1>
            <p className="text-gray-600 mt-1">{info.description}</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <ArticleList category={category === 'all' ? undefined : category} />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>🦐 苹果虾资讯 © 2026</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/**
 * 文章列表组件
 */
async function ArticleList({ category }: { category?: string }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = category
    ? `${apiUrl}/api/articles?category=${category}&limit=50`
    : `${apiUrl}/api/articles?limit=50`;

  let articles = [];
  try {
    const res = await fetch(url, {
      cache: 'no-store',
      next: { revalidate: 300 },
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
        <p>暂无文章</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {articles.map((article: Article) => (
        <article
          key={article.id}
          className="card hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start gap-4">
            {/* 缩略图（如果有） */}
            {article.image_urls && article.image_urls.length > 0 && (
              <div className="flex-shrink-0 w-32 h-24 bg-gray-200 rounded-lg overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={article.image_urls[0]}
                  alt={article.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            )}

            {/* 内容 */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
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
                <span className="text-xs text-gray-500">{article.source}</span>
                {article.published_at && (
                  <span className="text-xs text-gray-500">
                    · {new Date(article.published_at).toLocaleDateString('zh-CN')}
                  </span>
                )}
              </div>

              <h2 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
                {article.title}
              </h2>

              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {article.summary}
              </p>

              <div className="flex items-center gap-4">
                <Link
                  href={`/article/${article.id}`}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  阅读全文 →
                </Link>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  原文链接 ↗
                </a>
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
