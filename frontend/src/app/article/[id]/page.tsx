/**
 * 文章详情页
 */
import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Article } from '../../../types';

export default async function ArticlePage({ params }: { params: { id: string } }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  let article: Article | null = null;
  try {
    const res = await fetch(`${apiUrl}/api/articles/${params.id}`, {
      cache: 'no-store',
    });
    if (res.ok) {
      article = await res.json() as Article;
    }
  } catch (error) {
    console.error('获取文章失败:', error);
  }

  if (!article) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <Link href="/" className="text-blue-600 hover:text-blue-700">
            ← 返回首页
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <article className="bg-white rounded-lg shadow-md p-8">
          {/* 分类标签 */}
          <div className="flex items-center gap-2 mb-4">
            <span className={`text-xs px-3 py-1 rounded-full ${
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
            <span className="text-sm text-gray-500">{article.source}</span>
          </div>

          {/* 标题 */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {article.title}
          </h1>

          {/* 元数据 */}
          <div className="flex items-center gap-4 text-sm text-gray-500 mb-6 pb-6 border-b">
            {article.author && (
              <span>作者：{article.author}</span>
            )}
            {article.published_at && (
              <span>发布时间：{new Date(article.published_at).toLocaleDateString('zh-CN')}</span>
            )}
            {article.fetched_at && (
              <span>抓取时间：{new Date(article.fetched_at).toLocaleString('zh-CN')}</span>
            )}
          </div>

          {/* 图片廊 */}
          {article.image_urls && article.image_urls.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              {article.image_urls.slice(0, 6).map((url: string, index: number) => (
                <div key={index} className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={url}
                    alt={`${article.title} - 图片 ${index + 1}`}
                    className="w-full h-full object-cover"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              ))}
            </div>
          )}

          {/* 摘要 */}
          {article.summary && (
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">摘要</h2>
              <p className="text-gray-700 leading-relaxed">{article.summary}</p>
            </div>
          )}

          {/* 正文内容（如果有） */}
          {article.content ? (
            <div className="prose prose-lg max-w-none mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">正文</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {article.content}
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
              <p className="text-yellow-800">
                ℹ️ 正文内容暂未抓取，点击下方查看原文按钮访问原始文章。
              </p>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex flex-wrap gap-4 pt-6 border-t">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              查看原文
            </a>
            
            <button
              onClick={() => navigator.clipboard.writeText(article.url)}
              className="btn-outline inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              复制链接
            </button>

            <button
              onClick={() => {
                const shareUrl = encodeURIComponent(window.location.href);
                const shareText = encodeURIComponent(article.title);
                window.open(`https://weibo.com/share/share.php?url=${shareUrl}&title=${shareText}`, '_blank');
              }}
              className="btn-outline inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21.57 8.74c.18.66.14 1.46-.12 2.39-.26.93-.74 1.91-1.45 2.95-.76 1.09-1.59 2.01-2.5 2.76-.91.75-1.77 1.26-2.58 1.53-.81.27-1.51.32-2.09.15-.58-.17-1.07-.5-1.47-1-.4-.49-.67-1.07-.82-1.73-.15-.66-.14-1.46.03-2.39.17-.93.52-1.91 1.05-2.95.53-1.04 1.11-1.96 1.74-2.76.63-.8 1.25-1.42 1.86-1.86.61-.44 1.15-.66 1.62-.66.47 0 .86.15 1.17.45.31.3.53.7.66 1.2.13.5.16 1.07.09 1.71-.07.64-.24 1.32-.51 2.03-.27.71-.63 1.41-1.08 2.09-.45.68-.96 1.28-1.53 1.8-.57.52-1.17.92-1.8 1.2-.63.28-1.25.42-1.86.42-.61 0-1.15-.15-1.62-.45-.47-.3-.81-.73-1.02-1.29-.21-.56-.28-1.21-.21-1.95.07-.74.27-1.52.6-2.34.33-.82.78-1.62 1.35-2.4.57-.78 1.23-1.47 1.98-2.07.75-.6 1.55-1.07 2.4-1.41.85-.34 1.7-.51 2.55-.51.85 0 1.63.17 2.34.51.71.34 1.31.81 1.8 1.41.49.6.84 1.29 1.05 2.07.21.78.25 1.6.12 2.46z"/>
              </svg>
              分享到微博
            </button>
          </div>
        </article>

        {/* 相关文章（可选） */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">相关文章</h2>
          <RelatedArticles category={article.category} currentId={article.id.toString()} />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>🦐 苹果虾资讯 © 2026</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/**
 * 相关文章组件
 */
async function RelatedArticles({ category, currentId }: { category: string; currentId: string }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  let articles: Article[] = [];
  try {
    const res = await fetch(`${apiUrl}/api/articles?category=${category}&limit=4`, {
      cache: 'no-store',
    });
    if (res.ok) {
      const all = await res.json() as Article[];
      articles = all.filter((a) => a.id.toString() !== currentId.toString()).slice(0, 3);
    }
  } catch (error) {
    console.error('获取相关文章失败:', error);
  }

  if (articles.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {articles.map((article) => (
        <Link
          key={article.id}
          href={`/article/${article.id}`}
          className="card hover:shadow-lg transition-shadow"
        >
          <h3 className="text-base font-semibold text-gray-900 mb-2 line-clamp-2">
            {article.title}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {article.summary}
          </p>
        </Link>
      ))}
    </div>
  );
}
