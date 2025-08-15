import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Skeleton } from '../ui/skeleton';
import { 
  Search, 
  ExternalLink, 
  Clock, 
  Globe, 
  TrendingUp,
  BookOpen,
  MessageSquare,
  Loader2
} from 'lucide-react';
import { SearchResult } from '../../types';

export default function WebSearch() {
  const { addMessage } = useApp();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  const mockSearchResults: SearchResult[] = [
    {
      id: '1',
      title: 'OpenAI Announces GPT-4 Turbo with Latest AI Capabilities',
      url: 'https://openai.com/blog/gpt-4-turbo',
      snippet: 'OpenAI has released GPT-4 Turbo, featuring improved performance, longer context windows, and enhanced reasoning capabilities for better AI-powered applications.',
      source: 'OpenAI Blog'
    },
    {
      id: '2',
      title: 'Microsoft Copilot Integration Across Office Suite',
      url: 'https://microsoft.com/copilot',
      snippet: 'Microsoft integrates Copilot AI assistant across Word, Excel, PowerPoint, and Outlook, revolutionizing productivity and workflow automation.',
      source: 'Microsoft News'
    },
    {
      id: '3',
      title: 'Google Bard Updates: Multimodal AI and Real-time Information',
      url: 'https://blog.google/technology/ai/bard-updates',
      snippet: 'Google Bard now supports images, voice input, and real-time information retrieval, making it more versatile for complex queries and research tasks.',
      source: 'Google AI Blog'
    },
    {
      id: '4',
      title: 'AI Safety Guidelines: Industry Standards and Best Practices',
      url: 'https://aisafety.org/guidelines',
      snippet: 'Comprehensive guidelines for AI development focusing on safety, ethics, and responsible deployment of artificial intelligence systems.',
      source: 'AI Safety Institute'
    },
    {
      id: '5',
      title: 'The Future of Work: AI Tools Transforming Business Operations',
      url: 'https://techcrunch.com/ai-future-work',
      snippet: 'Analysis of how AI tools are reshaping business operations, from customer service automation to data analysis and decision-making processes.',
      source: 'TechCrunch'
    }
  ];

  const trendingSearches = [
    'AI productivity tools 2024',
    'ChatGPT vs Claude comparison',
    'Machine learning basics',
    'AI ethics guidelines',
    'Automation workflows',
    'Natural language processing'
  ];

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setQuery(searchQuery);

    // Add to search history
    setSearchHistory(prev => {
      const updated = [searchQuery, ...prev.filter(q => q !== searchQuery)];
      return updated.slice(0, 10); // Keep only last 10 searches
    });

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Filter and customize results based on query
    const filteredResults = mockSearchResults.map(result => ({
      ...result,
      title: result.title.includes('AI') ? result.title : `${searchQuery} - ${result.title}`,
      snippet: `${result.snippet} This result is specifically relevant to your search for "${searchQuery}".`
    }));

    setResults(filteredResults);
    setIsSearching(false);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(query);
  };

  const handleQuickSearch = (searchTerm: string) => {
    setQuery(searchTerm);
    performSearch(searchTerm);
  };

  const summarizeResults = () => {
    if (results.length === 0) return;

    const summary = `I searched for "${query}" and found ${results.length} relevant results. Here's a summary:\n\n${results.slice(0, 3).map((result, index) => 
      `${index + 1}. **${result.title}**\n   ${result.snippet}\n   Source: ${result.source}\n`
    ).join('\n')}`;

    addMessage(`Please analyze these search results for "${query}": ${summary}`, 'user');
  };

  const askAboutResult = (result: SearchResult) => {
    const prompt = `I found this search result about "${query}": "${result.title}" from ${result.source}. ${result.snippet} Can you help me understand this better and provide more context?`;
    addMessage(prompt, 'user');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center gap-2 mb-4">
          <Search className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">Web Search</h1>
        </div>
        <p className="text-muted-foreground">
          Search the web and get AI-powered insights on your results
        </p>
      </div>

      {/* Search Form */}
      <div className="p-6 border-b">
        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search the web..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-9"
              disabled={isSearching}
            />
          </div>
          <Button type="submit" disabled={!query.trim() || isSearching}>
            {isSearching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
        </form>

        {/* Quick Actions */}
        {results.length > 0 && (
          <div className="flex gap-2 mb-4">
            <Button variant="outline" size="sm" onClick={summarizeResults}>
              <MessageSquare className="h-4 w-4 mr-2" />
              Summarize Results
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href={`https://google.com/search?q=${encodeURIComponent(query)}`} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                View on Google
              </a>
            </Button>
          </div>
        )}

        {/* Trending Searches */}
        {results.length === 0 && !isSearching && (
          <div>
            <h3 className="font-medium mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Trending Searches
            </h3>
            <div className="flex flex-wrap gap-2">
              {trendingSearches.map((trend, index) => (
                <Badge 
                  key={index}
                  variant="outline" 
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                  onClick={() => handleQuickSearch(trend)}
                >
                  {trend}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Search History */}
        {searchHistory.length > 0 && (
          <div className="mt-4">
            <h3 className="font-medium mb-2 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Recent Searches
            </h3>
            <div className="flex flex-wrap gap-2">
              {searchHistory.slice(0, 5).map((historyItem, index) => (
                <Badge 
                  key={index}
                  variant="secondary" 
                  className="cursor-pointer hover:bg-secondary/80"
                  onClick={() => handleQuickSearch(historyItem)}
                >
                  {historyItem}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <ScrollArea className="flex-1 p-6">
        {isSearching && (
          <div className="space-y-4">
            {[...Array(5)].map((_, index) => (
              <Card key={index}>
                <CardHeader>
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-3 w-full mb-2" />
                  <Skeleton className="h-3 w-2/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!isSearching && results.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-muted-foreground">
                Found {results.length} results for "{query}"
              </p>
              <Badge variant="outline">
                <Globe className="h-3 w-3 mr-1" />
                Web Results
              </Badge>
            </div>

            {results.map((result, index) => (
              <Card key={result.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-base leading-tight mb-1">
                        <a 
                          href={result.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="hover:text-primary transition-colors"
                        >
                          {result.title}
                        </a>
                      </CardTitle>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{result.source}</span>
                        <ExternalLink className="h-3 w-3" />
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                      #{index + 1}
                    </span>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                    {result.snippet}
                  </p>
                  
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => askAboutResult(result)}
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Ask AI About This
                    </Button>
                    <Button variant="outline" size="sm" asChild>
                      <a href={result.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Visit Site
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!isSearching && results.length === 0 && query && (
          <div className="text-center py-12">
            <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No results found</h3>
            <p className="text-muted-foreground mb-4">
              Try different keywords or check your spelling
            </p>
            <Button onClick={() => setQuery('')}>
              <Search className="h-4 w-4 mr-2" />
              New Search
            </Button>
          </div>
        )}

        {!isSearching && results.length === 0 && !query && (
          <div className="text-center py-12">
            <div className="mb-6">
              <BookOpen className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-semibold mb-2">Web Search</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Search the web for the latest information, research topics, and get AI-powered insights on your results.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <Card className="p-4 text-left">
                <div className="flex items-center gap-3 mb-2">
                  <Search className="h-5 w-5 text-primary" />
                  <h4 className="font-medium">Smart Search</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Find relevant information quickly with intelligent search suggestions
                </p>
              </Card>

              <Card className="p-4 text-left">
                <div className="flex items-center gap-3 mb-2">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  <h4 className="font-medium">AI Analysis</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Get AI-powered summaries and insights from search results
                </p>
              </Card>

              <Card className="p-4 text-left">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  <h4 className="font-medium">Trending Topics</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Discover what's trending and explore popular search queries
                </p>
              </Card>

              <Card className="p-4 text-left">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="h-5 w-5 text-primary" />
                  <h4 className="font-medium">Search History</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Easily revisit your previous searches and build on your research
                </p>
              </Card>
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
