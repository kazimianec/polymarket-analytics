// Stats overview
export interface TopCategory {
  slug: string;
  label: string;
  volume: number;
  market_count: number;
}

export interface TrendingMarketSummary {
  id: string;
  question: string;
  yes_price: number;
  no_price: number;
  volume: number;
}

export interface StatsOverview {
  total_active_markets: number;
  total_volume: number;
  top_categories: TopCategory[];
  trending_markets: TrendingMarketSummary[];
}

// Trending markets
export interface TrendingMarket {
  id: string;
  question: string;
  yes_price: number;
  no_price: number;
  volume: number;
  liquidity: number;
  category: string | null;
  end_date: string | null;
  active: boolean;
  closed: boolean;
}

export interface TrendingMarketsResponse {
  markets: TrendingMarket[];
  total: number;
  has_more: boolean;
}

// Market detail
export interface MarketDetail {
  id: string;
  question: string;
  description: string;
  yes_price: number;
  no_price: number;
  volume: number;
  liquidity: number;
  category: string | null;
  end_date: string | null;
  outcomes: string[];
  active: boolean;
  closed: boolean;
  condition_id: string;
  clob_token_ids: string[];
}

// Market history
export interface PricePoint {
  timestamp: number;
  price: number;
}

export interface MarketHistory {
  history: PricePoint[];
}

// Categories
export interface Category {
  slug: string;
  label: string;
  volume: number;
  market_count: number;
}

export interface CategoriesResponse {
  categories: Category[];
}
