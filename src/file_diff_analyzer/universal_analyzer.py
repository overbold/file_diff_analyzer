#!/usr/bin/env python3
"""
Universal File Difference Analyzer

A universal analyzer for detecting differences between files of any type
without hardcoded patterns or specific file type dependencies.
"""

import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

from .analyzer import FileDiffAnalyzer
from .models import AnalysisConfig


class UniversalFileDiffAnalyzer:
    """Universal analyzer for detecting differences between files of any type"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.basic_analyzer = FileDiffAnalyzer(config)
        self.config = config or AnalysisConfig()
        
        # Universal patterns for analysis
        self.patterns = {
            'numbers': re.compile(r'\b\d+(?:\.\d+)?\b'),
            'versions': re.compile(r'\b(?:v|version|rev|revision)?\s*\d+(?:\.\d+)*(?:[a-zA-Z0-9-]*)\b', re.IGNORECASE),
            'dates': re.compile(r'\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b', re.IGNORECASE),
            'emails': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'urls': re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'),
            'ip_addresses': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'hex_values': re.compile(r'\b[0-9a-fA-F]{6,}\b'),
            'file_paths': re.compile(r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*|[\/](?:[^\/\0]+\/)*[^\/\0]*'),
            'code_blocks': re.compile(r'```[\s\S]*?```|`[^`]+`'),
            'markdown_headers': re.compile(r'^#{1,6}\s+.+$', re.MULTILINE),
            'numbered_lists': re.compile(r'^\d+[\.\)]\s+.+$', re.MULTILINE),
            'bullet_lists': re.compile(r'^[\-\*\+]\s+.+$', re.MULTILINE)
        }
    
    def add_file(self, file_path: str) -> 'UniversalFileDiffAnalyzer':
        """Adds a file for analysis"""
        self.basic_analyzer.add_file(file_path)
        return self
    
    def add_text(self, text: str, name: str = "text_segment") -> 'UniversalFileDiffAnalyzer':
        """Adds a text segment for analysis"""
        self.basic_analyzer.add_text(text, name)
        return self
    
    def analyze(self):
        """Performs basic analysis"""
        return self.basic_analyzer.analyze()
    
    def universal_analyze(self) -> Dict[str, Any]:
        """Performs universal analysis with detection of any type of changes"""
        if len(self.basic_analyzer._files) < 2:
            raise ValueError("Minimum 2 files required for comparison")
        
        basic_result = self.analyze()
        universal_analysis = self._perform_universal_analysis()
        
        universal_result = {
            "basic_analysis": {
                "similarity_percentage": basic_result.comparison_matrix[0].similarity_percentage,
                "difference_percentage": basic_result.comparison_matrix[0].difference_percentage,
                "is_significantly_different": basic_result.comparison_matrix[0].is_significantly_different,
                "common_words": basic_result.comparison_matrix[0].common_words,
                "unique_words_file1": basic_result.comparison_matrix[0].unique_words_file1,
                "unique_words_file2": basic_result.comparison_matrix[0].unique_words_file2
            },
            "universal_analysis": universal_analysis,
            "summary": {
                "real_changes_count": len(universal_analysis["real_changes"]),
                "structural_changes_count": len(universal_analysis["structural_changes"]),
                "overall_assessment": self._get_universal_assessment(universal_analysis),
                "change_impact": self._get_universal_change_impact(universal_analysis),
                "change_categories": self._get_change_categories(universal_analysis)
            }
        }
        
        return universal_result
    
    def _perform_universal_analysis(self) -> Dict[str, Any]:
        """Performs universal analysis with smart detection for similar files"""
        if len(self.basic_analyzer._files) != 2:
            return {"error": "Exactly 2 files required for universal analysis"}
        
        file1 = self.basic_analyzer._files[0]
        file2 = self.basic_analyzer._files[1]
        
        # Get basic similarity from basic analyzer
        basic_result = self.basic_analyzer.analyze()
        similarity = basic_result.comparison_matrix[0].similarity_percentage
        
        # If files are very similar (95%+), use detailed line-by-line analysis
        if similarity >= 95.0:
            return self._detailed_line_analysis(file1, file2)
        else:
            # For less similar files, use basic word-based analysis
            return self._basic_word_analysis(file1, file2)
    
    def _detailed_line_analysis(self, file1, file2) -> Dict[str, Any]:
        """Detailed line-by-line analysis for similar files (95%+ similarity)"""
        lines1 = file1.content.split('\n')
        lines2 = file2.content.split('\n')
        
        real_changes = []
        structural_changes = []
        
        # Use SequenceMatcher for precise line-level diff
        sm = SequenceMatcher(None, lines1, lines2, autojunk=False)
        opcodes = sm.get_opcodes()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue  # Skip identical lines
                
            elif tag == 'insert':
                # New lines added
                for j in range(j1, j2):
                    if lines2[j].strip():
                        real_changes.append(self._create_simple_change("", lines2[j], 'line_addition'))
                        
            elif tag == 'delete':
                # Lines removed
                for i in range(i1, i2):
                    if lines1[i].strip():
                        real_changes.append(self._create_simple_change(lines1[i], "", 'line_deletion'))
                        
            elif tag == 'replace':
                # Lines were replaced - analyze each pair
                common_len = min(i2 - i1, j2 - j1)
                
                # Compare corresponding lines
                for off in range(common_len):
                    old_line = lines1[i1 + off]
                    new_line = lines2[j1 + off]
                    
                    if old_line.strip() != new_line.strip():
                        # This is a real content change
                        change = self._analyze_universal_line_change(old_line, new_line)
                        if change:
                            real_changes.append(change)
                        else:
                            real_changes.append(self._create_simple_change(old_line, new_line, 'content_modification'))
                
                # Handle extra lines as insertions/deletions
                if i2 - i1 > common_len:
                    for i in range(i1 + common_len, i2):
                        if lines1[i].strip():
                            real_changes.append(self._create_simple_change(lines1[i], "", 'line_deletion'))
                            
                if j2 - j1 > common_len:
                    for j in range(j1 + common_len, j2):
                        if lines2[j].strip():
                            real_changes.append(self._create_simple_change("", lines2[j], 'line_addition'))
        
        return {
            "real_changes": real_changes,
            "structural_changes": structural_changes,
            "total_changes": len(real_changes) + len(structural_changes),
            "analysis_method": "detailed_line_diff",
            "similarity_percentage": "95%+ (detailed analysis)"
        }
    
    def _basic_word_analysis(self, file1, file2) -> Dict[str, Any]:
        """Basic word-based analysis for less similar files"""
        # Extract words from both files
        words1 = set(file1.content.lower().split())
        words2 = set(file2.content.lower().split())
        
        # Calculate differences
        added_words = words2 - words1
        removed_words = words1 - words2
        
        real_changes = []
        
        if added_words:
            real_changes.append({
                "type": "words_added",
                "description": f"Added {len(added_words)} new words",
                "old_content": "",
                "new_content": ", ".join(sorted(added_words)[:10]) + ("..." if len(added_words) > 10 else ""),
                "impact": "moderate",
                "change_category": "content_addition"
            })
        
        if removed_words:
            real_changes.append({
                "type": "words_removed",
                "description": f"Removed {len(removed_words)} words",
                "old_content": ", ".join(sorted(removed_words)[:10]) + ("..." if len(removed_words) > 10 else ""),
                "new_content": "",
                "impact": "moderate",
                "change_category": "content_deletion"
            })
        
        return {
            "real_changes": real_changes,
            "structural_changes": [],
            "total_changes": len(real_changes),
            "analysis_method": "basic_word_diff",
            "similarity_percentage": "less than 95% (basic analysis)"
        }
    
    def _normalize_text(self, text: str) -> str:
        """Step 1: Text normalization and unification"""
        
        # Unify line endings: \r\n|\r|\n → \n
        text = re.sub(r'\r\n|\r|\n', '\n', text)
        
        # Normalize whitespace: \s+ inside lines → single space
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove non-printable characters, normalize internal whitespace
            line = re.sub(r'[^\x20-\x7E\xA0-\uFFFF]', '', line)  # Keep printable + extended
            line = re.sub(r'\s+', ' ', line)  # Multiple spaces → single space
            line = line.strip()
            if line:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _reflow_text(self, text: str) -> str:
        """Step 2: Text reflow - for structured text like roadmaps, preserve line structure"""
        # For structured text (roadmaps, documentation), don't reflow - preserve line structure
        return text
    
    def _should_join_lines(self, prev_line: str, current_line: str) -> bool:
        """Determine if two lines should be joined into one paragraph"""
        # If previous line doesn't end with sentence ending
        if not re.search(r'[.!?…"\'\)]\s*$', prev_line):
            # And current line starts with lowercase or small word
            if re.match(r'^[a-zа-я]', current_line) or len(current_line.split()[0]) <= 3:
                return True
        
        # Handle hyphenated words
        if re.search(r'[A-Za-zА-Яа-я]-\s*$', prev_line):
            return True
        
        return False
    
    def _segment_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Step 3: Segment text into structural blocks"""
        lines = text.split('\n')
        blocks = []
        current_block = []
        current_type = None
        
        for line in lines:
            if not line.strip():
                if current_block:
                    blocks.append({
                        'type': current_type or 'text',
                        'content': '\n'.join(current_block),
                        'lines': current_block
                    })
                    current_block = []
                    current_type = None
                continue
            
            # Detect block type
            block_type = self._detect_block_type(line)
            
            if block_type != current_type and current_block:
                # End current block
                blocks.append({
                    'type': current_type or 'text',
                    'content': '\n'.join(current_block),
                    'lines': current_block
                })
                current_block = []
            
            current_type = block_type
            current_block.append(line)
        
        # Handle last block
        if current_block:
            blocks.append({
                'type': current_type or 'text',
                'content': '\n'.join(current_block),
                'lines': current_block
            })
        
        return blocks
    
    def _detect_block_type(self, line: str) -> str:
        """Detect the type of a text block"""
        # Headers
        if re.match(r'^#{1,6}\s', line):
            return 'header'
        if re.match(r'^\d+[\.\)]\s', line):
            return 'header'
        if line.isupper() and len(line) < 100:
            return 'header'
        
        # Lists
        if re.match(r'^[-*+]\s', line):
            return 'list'
        if re.match(r'^\d+\.\s', line):
            return 'list'
        
        # Code blocks
        if re.match(r'^\s{4,}', line) or '|' in line and line.count('|') > 2:
            return 'code'
        
        # Quotes
        if re.match(r'^>\s', line):
            return 'quote'
        
        return 'text'
    
    def _greedy_match_by_signature(self, blocks1: List[Dict], blocks2: List[Dict]) -> Dict[int, int]:
        """Step 4: Greedy block matching by signature (Jaccard similarity)"""
        matches = {}
        
        for i, block1 in enumerate(blocks1):
            best_match = -1
            best_similarity = 0
            
            for j, block2 in enumerate(blocks2):
                if j in matches.values():  # Already matched
                    continue
                
                similarity = self._calculate_block_similarity(block1, block2)
                if similarity > best_similarity and similarity >= 0.6:  # Lower threshold to detect changes
                    best_similarity = similarity
                    best_match = j
            
            if best_match != -1:
                matches[i] = best_match
        
        return matches
    
    def _calculate_block_similarity(self, block1: Dict, block2: Dict) -> float:
        """Calculate Jaccard similarity between two blocks"""
        words1 = set(re.findall(r'\w+', block1['content'].lower()))
        words2 = set(re.findall(r'\w+', block2['content'].lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _lcs_diff_blocks(self, blocks1: List[Dict], blocks2: List[Dict], matches: Dict[int, int]) -> List[Dict]:
        """Step 5: LCS diff on blocks"""
        # Create ordered sequences based on matches
        seq1 = []
        seq2 = []
        
        # Add matched blocks in order
        for i, block1 in enumerate(blocks1):
            if i in matches:
                seq1.append(('matched', i))
                seq2.append(('matched', matches[i]))
        
        # Add unmatched blocks
        unmatched1 = [i for i in range(len(blocks1)) if i not in matches]
        unmatched2 = [i for i in range(len(blocks2)) if i not in matches.values()]
        
        seq1.extend([('unmatched', i) for i in unmatched1])
        seq2.extend([('unmatched', i) for i in unmatched2])
        
        # Generate operations
        operations = []
        
        # Process matched blocks
        for (type1, idx1), (type2, idx2) in zip(seq1, seq2):
            if type1 == 'matched' and type2 == 'matched':
                similarity = self._calculate_block_similarity(blocks1[idx1], blocks2[idx2])
                if similarity >= 0.98:  # Almost identical
                    operations.append({
                        'type': 'KEEP',
                        'content': blocks1[idx1]['content'],
                        'score': similarity
                    })
                else:  # Similar but with changes
                    operations.append({
                        'type': 'MODIFY_BLOCK',
                        'old_content': blocks1[idx1]['content'],
                        'new_content': blocks2[idx2]['content'],
                        'old_type': blocks1[idx1]['type'],
                        'new_type': blocks2[idx2]['type'],
                        'score': similarity
                    })
        
        # Add unmatched as INSERT/DELETE
        for idx in unmatched1:
            operations.append({
                'type': 'DELETE_BLOCK',
                'content': blocks1[idx]['content'],
                'score': 0.0
            })
        
        for idx in unmatched2:
            operations.append({
                'type': 'INSERT_BLOCK',
                'content': blocks2[idx]['content'],
                'score': 0.0
            })
        
        return operations
    
    def _analyze_block_modification(self, op: Dict) -> List[Dict]:
        """Analyze detailed changes within a modified block"""
        changes = []
        
        # Split into lines for more granular analysis
        lines1 = op['old_content'].split('\n')
        lines2 = op['new_content'].split('\n')
        
        # Use SequenceMatcher for line-level diff within the block
        sm = SequenceMatcher(None, lines1, lines2, autojunk=False)
        opcodes = sm.get_opcodes()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue  # Skip identical lines
                
            elif tag == 'insert':
                # New lines added
                for j in range(j1, j2):
                    if lines2[j].strip():
                        changes.append(self._create_simple_change("", lines2[j], 'line_addition'))
                        
            elif tag == 'delete':
                # Lines removed
                for i in range(i1, i2):
                    if lines1[i].strip():
                        changes.append(self._create_simple_change(lines1[i], "", 'line_deletion'))
                        
            elif tag == 'replace':
                # Lines were replaced - analyze each pair
                common_len = min(i2 - i1, j2 - j1)
                
                # Compare corresponding lines
                for off in range(common_len):
                    old_line = lines1[i1 + off]
                    new_line = lines2[j1 + off]
                    
                    if old_line.strip() != new_line.strip():
                        # This is a real content change
                        change = self._analyze_universal_line_change(old_line, new_line)
                        if change:
                            changes.append(change)
                        else:
                            changes.append(self._create_simple_change(old_line, new_line, 'content_modification'))
                
                # Handle extra lines as insertions/deletions
                if i2 - i1 > common_len:
                    for i in range(i1 + common_len, i2):
                        if lines1[i].strip():
                            changes.append(self._create_simple_change(lines1[i], "", 'line_deletion'))
                            
                if j2 - j1 > common_len:
                    for j in range(j1 + common_len, j2):
                        if lines2[j].strip():
                            changes.append(self._create_simple_change("", lines2[j], 'line_addition'))
        
        return changes
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        # Simple sentence splitting by punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_block_change(self, old_content: str, new_content: str, change_type: str) -> Dict[str, Any]:
        """Create a block-level change description"""
        if change_type == 'block_addition':
            return {
                "type": "block_addition",
                "description": f"Block added: {new_content[:100]}...",
                "old_content": "",
                "new_content": new_content,
                "impact": "moderate",
                "change_category": "content_addition"
            }
        elif change_type == 'block_deletion':
            return {
                "type": "block_deletion",
                "description": f"Block removed: {old_content[:100]}...",
                "old_content": old_content,
                "new_content": "",
                "impact": "moderate",
                "change_category": "content_deletion"
            }
        else:
            return {
                "type": "block_modification",
                "description": "Block content modified",
                "old_content": old_content,
                "new_content": new_content,
                "impact": "moderate",
                "change_category": "content_modification"
            }
    
    def _create_move_change(self, op: Dict) -> Dict[str, Any]:
        """Create a move operation description"""
        return {
            "type": "structural_move",
            "description": "Block moved to different position",
            "content": op['content'],
            "impact": "none",
            "change_category": "formatting"
        }
    
    def _analyze_universal_line_change(self, old_line: str, new_line: str) -> Optional[Dict[str, Any]]:
        """Universal analysis of specific line change"""
        old_line = old_line.strip()
        new_line = new_line.strip()

        if not old_line or not new_line:
            return None

        # Only analyze short lines to avoid false positives
        if len(old_line) > 200 or len(new_line) > 200:
            return None

        # Try to detect specific pattern changes first
        change_info = self._detect_pattern_changes(old_line, new_line)
        if change_info:
            return change_info

        # Try general changes
        general = self._analyze_general_changes(old_line, new_line)
        if general:
            return general

        # Return None to use default content_modification
        return None


    
    def _detect_pattern_changes(self, old_line: str, new_line: str) -> Optional[Dict[str, Any]]:
        """Detects changes based on universal patterns"""
        numbers_old = self.patterns['numbers'].findall(old_line)
        numbers_new = self.patterns['numbers'].findall(new_line)
        
        if numbers_old and numbers_new and numbers_old != numbers_new:
            return self._create_numeric_change(old_line, new_line, numbers_old, numbers_new)
        
        versions_old = self.patterns['versions'].findall(old_line)
        versions_new = self.patterns['versions'].findall(new_line)
        
        if versions_old and versions_new and versions_old != versions_new:
            return self._create_version_change(old_line, new_line, versions_old, versions_new)
        
        dates_old = self.patterns['dates'].findall(old_line)
        dates_new = self.patterns['dates'].findall(new_line)
        
        if dates_old and dates_new and dates_old != dates_new:
            return self._create_date_change(old_line, new_line, dates_old, dates_new)
        
        urls_old = self.patterns['urls'].findall(old_line)
        urls_new = self.patterns['urls'].findall(new_line)
        
        if urls_old and urls_new and urls_old != urls_new:
            return self._create_url_change(old_line, new_line, urls_old, urls_new)
        
        emails_old = self.patterns['emails'].findall(old_line)
        emails_new = self.patterns['emails'].findall(new_line)
        
        if emails_old and emails_new and emails_old != emails_new:
            return self._create_email_change(old_line, new_line, emails_old, emails_new)
        
        return None
    
    def _create_numeric_change(self, old_line: str, new_line: str, old_numbers: List[str], new_numbers: List[str]) -> Dict[str, Any]:
        return {
            "type": "numeric_change",
            "description": f"Numeric value changed from {', '.join(old_numbers)} to {', '.join(new_numbers)}",
            "old_content": old_line,
            "new_content": new_line,
            "old_values": old_numbers,
            "new_values": new_numbers,
            "impact": self._assess_numeric_impact(old_numbers, new_numbers),
            "change_category": "data_modification"
        }
    
    def _create_version_change(self, old_line: str, new_line: str, old_versions: List[str], new_versions: List[str]) -> Dict[str, Any]:
        return {
            "type": "version_change",
            "description": f"Version changed from {', '.join(old_versions)} to {', '.join(new_versions)}",
            "old_content": old_line,
            "new_content": new_line,
            "old_values": old_versions,
            "new_values": new_versions,
            "impact": self._assess_version_impact(old_versions, new_versions),
            "change_category": "version_update"
        }
    
    def _create_date_change(self, old_line: str, new_line: str, old_dates: List[str], new_dates: List[str]) -> Dict[str, Any]:
        return {
            "type": "date_change",
            "description": f"Date changed from {', '.join(old_dates)} to {', '.join(new_dates)}",
            "old_content": old_line,
            "new_content": new_line,
            "old_values": old_dates,
            "new_values": new_dates,
            "impact": "minor",
            "change_category": "date_update"
        }
    
    def _create_url_change(self, old_line: str, new_line: str, old_urls: List[str], new_urls: List[str]) -> Dict[str, Any]:
        return {
            "type": "url_change",
            "description": f"URL changed from {', '.join(old_urls)} to {', '.join(new_urls)}",
            "old_content": old_line,
            "new_content": new_line,
            "old_values": old_urls,
            "new_values": new_urls,
            "impact": "moderate",
            "change_category": "url_update"
        }
    
    def _create_email_change(self, old_line: str, new_line: str, old_emails: List[str], new_emails: List[str]) -> Dict[str, Any]:
        return {
            "type": "email_change",
            "description": f"Email changed from {', '.join(old_emails)} to {', '.join(new_emails)}",
            "old_content": old_line,
            "new_content": new_line,
            "old_values": old_emails,
            "new_values": new_emails,
            "impact": "moderate",
            "change_category": "contact_update"
        }
    
    def _assess_numeric_impact(self, old_numbers: List[str], new_numbers: List[str]) -> str:
        try:
            old_vals = [float(n) for n in old_numbers]
            new_vals = [float(n) for n in new_numbers]
            if len(old_vals) != len(new_vals):
                return "moderate"
            max_change = max(abs((new - old) / old) if old != 0 else float('inf') for old, new in zip(old_vals, new_vals))
            if max_change > 1.0:
                return "major"
            elif max_change > 0.1:
                return "moderate"
            else:
                return "minor"
        except (ValueError, ZeroDivisionError):
            return "moderate"
    
    def _create_simple_change(self, old_line: str, new_line: str, change_type: str) -> Dict[str, Any]:
        if change_type == 'line_addition':
            return {
                "type": "line_addition",
                "description": f"Line added: {new_line.strip()}",
                "old_content": "",
                "new_content": new_line,
                "impact": "minor",
                "change_category": "content_addition"
            }
        elif change_type == 'line_deletion':
            return {
                "type": "line_deletion",
                "description": f"Line removed: {old_line.strip()}",
                "old_content": old_line,
                "new_content": "",
                "impact": "minor",
                "change_category": "content_deletion"
            }
        else:
            return {
                "type": "content_modification",
                "description": f"Content changed from '{old_line.strip()}' to '{new_line.strip()}'",
                "old_content": old_line,
                "new_content": new_line,
                "impact": "moderate",
                "change_category": "content_modification"
            }
    
    def _assess_version_impact(self, old_versions: List[str], new_versions: List[str]) -> str:
        try:
            for old, new in zip(old_versions, new_versions):
                old_parts = old.replace('v', '').replace('version', '').replace('rev', '').replace('revision', '').strip().split('.')
                new_parts = new.replace('v', '').replace('version', '').replace('rev', '').replace('revision', '').strip().split('.')
                if len(old_parts) >= 1 and len(new_parts) >= 1:
                    old_major = int(old_parts[0]) if old_parts[0].isdigit() else 0
                    new_major = int(new_parts[0]) if new_parts[0].isdigit() else 0
                    if new_major > old_major:
                        return "major"
                    elif len(old_parts) >= 2 and len(new_parts) >= 2:
                        old_minor = int(old_parts[1]) if old_parts[1].isdigit() else 0
                        new_minor = int(new_parts[1]) if new_parts[1].isdigit() else 0
                        if new_minor > old_minor:
                            return "moderate"
            return "minor"
        except (ValueError, IndexError):
            return "moderate"
    
    def _analyze_general_changes(self, old_line: str, new_line: str) -> Dict[str, Any]:
        if self._is_numbered_item(old_line) and self._is_numbered_item(new_line):
            old_num = self._extract_number(old_line)
            new_num = self._extract_number(new_line)
            if old_num != new_num:
                return {
                    "type": "numbering_update",
                    "description": f"Numbering changed from {old_num} to {new_num}",
                    "old_content": old_line,
                    "new_content": new_line,
                    "impact": "none",
                    "change_category": "formatting"
                }
        if self._is_bullet_item(old_line) and self._is_bullet_item(new_line):
            return {
                "type": "list_item_change",
                "description": "List item changed",
                "old_content": old_line,
                "new_content": new_line,
                "impact": "minor",
                "change_category": "content"
            }
        return {
            "type": "content_modification",
            "description": "Line content modified",
            "old_content": old_line,
            "new_content": new_line,
            "impact": "moderate",
            "change_category": "content"
        }
    
    def _is_numbered_item(self, line: str) -> bool:
        return bool(re.match(r'^\d+[\.\)]\s+', line))
    
    def _is_bullet_item(self, line: str) -> bool:
        return bool(re.match(r'^[\-\*\+]\s+', line))
    
    def _extract_number(self, line: str) -> Optional[int]:
        match = re.match(r'^(\d+)[\.\)]\s+', line)
        return int(match.group(1)) if match else None
    
    def _analyze_structural_shifts_simple(self, lines1: List[str], lines2: List[str], insertions: List[tuple], deletions: List[tuple]) -> List[Dict[str, Any]]:
        """Analyzes structural shifts caused by insertions and deletions"""
        shifts = []
        
        # Calculate shift for each line based on insertions/deletions before it
        for i, line1 in enumerate(lines1):
            if not line1.strip():
                continue
            
            # Find this line in lines2
            for j, line2 in enumerate(lines2):
                if line1.strip() == line2.strip():
                    # Calculate how much this line shifted
                    shift_distance = abs(j - i)
                    
                    # Only report significant shifts (more than 1 position)
                    if shift_distance > 1:
                        shifts.append({
                            "type": "structural_shift",
                            "description": f"Line shifted from position {i+1} to {j+1} due to insertions/deletions",
                            "content": line1.strip(),
                            "old_position": i + 1,
                            "new_position": j + 1,
                            "shift_distance": shift_distance,
                            "impact": "none",
                            "change_category": "formatting"
                        })
                    break
        
        return shifts
    
    def _get_universal_assessment(self, analysis: Dict[str, Any]) -> str:
        if not analysis["real_changes"] and not analysis["structural_changes"]:
            return "No significant changes detected"
        elif len(analysis["real_changes"]) <= 2 and not analysis["structural_changes"]:
            return "Minor changes only"
        elif len(analysis["real_changes"]) > 10:
            return "Major content changes"
        else:
            return "Moderate changes detected"
    
    def _get_universal_change_impact(self, analysis: Dict[str, Any]) -> str:
        impacts = [c.get("impact", "minor") for c in analysis["real_changes"]]
        if "major" in impacts:
            return "major"
        elif "moderate" in impacts:
            return "moderate"
        else:
            return "minor"
    
    def _get_change_categories(self, analysis: Dict[str, Any]) -> List[str]:
        categories = set(c.get("change_category", "other") for c in analysis["real_changes"])
        return sorted(list(categories))
