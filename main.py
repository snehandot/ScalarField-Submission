import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import anthropic
import threading
from test2 import context

class ClaudeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ScalarField QA Interface")
        self.root.geometry("800x600")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic()

        
        self.setup_ui()
    
    def setup_ui(self):
        # Query input section
        query_frame = ttk.Frame(self.root, padding="10")
        query_frame.pack(fill=tk.X)
        
        ttk.Label(query_frame, text="Enter your query:").pack(anchor=tk.W)
        
        self.query_entry = tk.Entry(query_frame, font=("Arial", 12))
        self.query_entry.pack(fill=tk.X, pady=(5, 10))
        self.query_entry.bind("<Return>", lambda e: self.send_query())
        
        # Send button
        self.send_button = ttk.Button(query_frame, text="Send Query", command=self.send_query)
        self.send_button.pack()
        
        # Response section
        response_frame = ttk.Frame(self.root, padding="10")
        response_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(response_frame, text="Answer:").pack(anchor=tk.W)
        
        self.answer_text = scrolledtext.ScrolledText(
            response_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Arial", 11)
        )
        self.answer_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Citations section
        ttk.Label(response_frame, text="Citations:").pack(anchor=tk.W)
        
        self.citations_text = scrolledtext.ScrolledText(
            response_frame, 
            height=6, 
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black"
        )
        self.citations_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Thinking section
        ttk.Label(response_frame, text="CoT Process:").pack(anchor=tk.W)
        
        self.thinking_text = scrolledtext.ScrolledText(
            response_frame, 
            height=6, 
            wrap=tk.WORD,
            font=("Arial", 9),
            bg="#f8f8f8",
            fg="black"
        )
        self.thinking_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def send_query(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        # Disable button and show loading
        self.send_button.config(state="disabled", text="Processing...")
        self.answer_text.delete(1.0, tk.END)
        self.citations_text.delete(1.0, tk.END)
        self.thinking_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "Processing your query...")
        docs=context(query)
        # Run API call in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.make_api_call, args=(query,docs,))
        thread.daemon = True
        thread.start()
    
    def make_api_call(self, query, docs):
        try:
            # Comprehensive CoT prompt for SEC filing analysis
            cot_prompt = f"""You are an expert financial analyst with deep expertise in SEC filings analysis. You will analyze the provided SEC filing documents and answer the user's specific question using a systematic Chain of Thought approach.

## CHAIN OF THOUGHT ANALYSIS FRAMEWORK:

### Step 1: Document Understanding
- First, identify what type of SEC filing(s) you're analyzing (10-K, 10-Q, 8-K, etc.)
- Understand the reporting period and company context
- Note any special circumstances or events mentioned

### Step 2: Question Decomposition
- Break down the user's question into specific analytical components
- Identify what financial metrics, trends, or insights are being requested
- Determine what sections of the filing are most relevant

### Step 3: Data Extraction and Verification
- Extract relevant financial data, ratios, and key metrics from the filing
- Cross-reference numbers across different sections for consistency
- Note any accounting changes, restatements, or unusual items
- Identify trends over multiple periods if available

### Step 4: Financial Analysis Framework
Apply relevant analysis techniques:
- **Liquidity Analysis**: Current ratio, quick ratio, cash flow analysis
- **Profitability Analysis**: Margins, ROE, ROA, earnings quality
- **Leverage Analysis**: Debt ratios, coverage ratios, credit metrics
- **Operational Analysis**: Revenue trends, cost structure, segment performance
- **Risk Assessment**: Risk factors, contingencies, off-balance sheet items
- **Management Discussion**: MD&A insights, forward guidance, strategy

### Step 5: Industry and Market Context
- Consider industry-specific metrics and benchmarks
- Evaluate competitive positioning if mentioned
- Assess market conditions and their impact on the company

### Step 6: Risk and Red Flag Analysis
- Identify potential accounting red flags
- Assess going concern issues if any
- Evaluate disclosure quality and transparency
- Note any regulatory or compliance issues

### Step 7: Synthesis and Conclusion
- Synthesize findings to directly answer the user's question
- Provide quantitative evidence with specific numbers and calculations
- Highlight key insights and their implications
- Identify limitations of the analysis

### Step 8: Recommendations and Next Steps
- Provide actionable insights based on the analysis
- Suggest additional areas for investigation if relevant
- Highlight key metrics to monitor going forward

## ANALYSIS REQUIREMENTS:
- Always cite specific page numbers, sections, or line items from the filing
- Provide exact numerical data with proper context
- Calculate relevant ratios and metrics when applicable
- Compare current period to prior periods when data is available
- Highlight any unusual or noteworthy items
- Use professional financial terminology appropriately
- Ensure all conclusions are supported by evidence from the filing

## USER QUESTION TO ANALYZE:
{query}

Now, please analyze the provided SEC filing documents using this comprehensive framework and provide a detailed response to the user's question. Make sure to follow each step systematically and provide specific citations from the documents."""
            print(query,docs)
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "text",
                                    "media_type": "text/plain",
                                    "data": f"{docs[:100000]}"
                                },
                                "title": "My Document",
                                "context": "This is a SEC Filings document.",
                                "citations": {"enabled": True}
                            },
                            {
                                "type": "text",
                                "text": cot_prompt
                            }
                        ]
                    }
                ]
            )
            # Process response in main thread
            self.root.after(0, self.display_response, response)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.display_error, error_msg)
    
    def display_response(self, response):
        # Clear previous content
        self.answer_text.delete(1.0, tk.END)
        self.citations_text.delete(1.0, tk.END)
        self.thinking_text.delete(1.0, tk.END)
        
        # Extract answer text, citations, and thinking
        answer_parts = []
        citations = []
        thinking_content = ""
        
        for block in response.content:
            if block.type == 'text':
                answer_parts.append(block.text)
                
                # Extract citations if present
                if hasattr(block, 'citations') and block.citations:
                    for citation in block.citations:
                        citations.append({
                            'text': block.text,
                            'cited_text': citation.cited_text,
                            'document_title': citation.document_title,
                            'start_char': citation.start_char_index,
                            'end_char': citation.end_char_index
                        })
            elif block.type == 'thinking':
                thinking_content = block.thinking
        
        # Display answer
        full_answer = ''.join(answer_parts)
        self.answer_text.insert(tk.END, full_answer)
        
        # Display citations
        if citations:
            for i, citation in enumerate(citations, 1):
                citation_text = f"Citation {i}:\n"
                citation_text += f"  Text: \"{citation['text'].strip()}\"\n"
                citation_text += f"  Source: \"{citation['cited_text']}\"\n"
                citation_text += f"  Document: {citation['document_title']}\n"
                citation_text += f"  Position: {citation['start_char']}-{citation['end_char']}\n\n"
                self.citations_text.insert(tk.END, citation_text)
        else:
            self.citations_text.insert(tk.END, "No citations found in the response.")
        
        # Display thinking process
        if thinking_content:
            self.thinking_text.insert(tk.END, thinking_content)
        else:
            self.thinking_text.insert(tk.END, "No thinking process available for this response.")
        
        # Re-enable button
        self.send_button.config(state="normal", text="Send Query")
    
    def display_error(self, error_msg):
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, error_msg)
        self.send_button.config(state="normal", text="Send Query")

def main():
    root = tk.Tk()
    app = ClaudeUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()