\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sprawko}[sprawko]
\RequirePackage[polish]{babel}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}

\def\@baseclass{mwart}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\@baseclass}}
% linter detects 'openright' as unused option
% \PassOptionsToClass{a4paper,twoside,openright,12pt}{\@baseclass}
\PassOptionsToClass{a4paper,oneside,10pt,twocolumn}{\@baseclass}
\ProcessOptions

\LoadClass[
    10pt,
    oneside,
    twocolumn
]{\@baseclass}

\RequirePackage[
    a4paper,
    left=2.0cm,
    right=2.0cm,
    top=2.0cm,
    bottom=2.0cm,
    marginparwidth=2.0cm
]{geometry}

\pagenumbering{arabic}

% ----------------------- bajery -----------------------------

% common packages

\RequirePackage{amsmath}    % Basic mathematical typesetting
\RequirePackage{amssymb}    % Advanced math symbols
\RequirePackage{amsthm}     % Theorems typesetting
\RequirePackage{array}      % Advanced table column formats
\RequirePackage[            % Bibliography in biber
    backend=biber,
    style=ieee
    % dashed=false
]{biblatex}
\RequirePackage[            % Custom figure and table captions
    font=small,
    labelfont=bf,
    labelsep=period,
    justification=centering,
    width=\textwidth
]{caption}
\RequirePackage{chngcntr}   % Per-section counters
\RequirePackage{enumitem}   % Itemize/enumrate
\RequirePackage{fancyhdr}   % Custom header/footer styles
\RequirePackage{graphicx}   % Enhanced images support
\RequirePackage{ifluatex}   % LuaTeX-specific options
\RequirePackage{ifpdf}      % pdfTeX-specific options
\RequirePackage{ifxetex}    % XeTeX-specific options
\RequirePackage{kantlipsum} % English kantian-style lipsum
\RequirePackage{lipsum}     % Lorem ipsum
\RequirePackage{listings}   % Code listings
\RequirePackage{longtable}  % Multi-page tables
\RequirePackage{multirow}   % Advanced table cells
\RequirePackage{setspace}   % Set space between lines
\RequirePackage{scrextend}  % Allows \addmargin environment
\RequirePackage{tocloft}    % Custom ToC/LoF/LoT
\RequirePackage{url}        % URL-sensitive line breaks
\RequirePackage{xkeyval}    % Keys and class parameters
\RequirePackage{xspace}     % Remove duplicated spaces

% + some extras
\RequirePackage{float}
\RequirePackage{booktabs}
\RequirePackage{caption}
\RequirePackage{subcaption}
% not needed
\RequirePackage{minted}
\RequirePackage{placeins}
\RequirePackage{adjustbox}
% option clash for package xcolor
% \RequirePackage[table, xcdraw]{xcolor}
\RequirePackage{caption}
\RequirePackage{textcomp, gensymb}

\RequirePackage{csquotes}
\RequirePackage{makecell}
\RequirePackage{newclude}


%--------------------------------
% Produce clickable hyperlinks
% in ToC, LoF and LoT
%--------------------------------
\RequirePackage{hyperref}
\hypersetup{
    colorlinks,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black
}


% absolute figire / table numbering
\counterwithout{figure}{section}
\counterwithout{table}{section}

%--------------------------------
% Table of Contents setup
%--------------------------------
\setlength{\cftbeforesecskip}{2pt}
\renewcommand{\cftsecfont}{\bf\normalsize}
\renewcommand{\cftsecpagefont}{\normalfont}
\renewcommand{\cftsecleader}{\cftdotfill{\cftsecdotsep}}
\renewcommand{\cftsecdotsep}{\cftdotsep}

%--------------------------------
% Header & footer
%--------------------------------
\SetSectionFormatting{section}{0.5cm}{\FormatHangHeading{\Large}}{0.5cm}
\let\oldsection\section
\renewcommand{\section}{
	\thispagestyle{plain}
	\oldsection
}

\fancypagestyle{plain}{
	\fancyhf{}
	\renewcommand{\headrulewidth}{0pt}
	\fancyfoot[C]{\thepage}
}

\fancypagestyle{headings}{
	\fancyhead{}
	\renewcommand{\headrulewidth}{1pt}
	\fancyheadoffset{0cm}
	\fancyhead[RO]{\nouppercase{\thesection.\hspace{8pt}\leftmark}}
	\fancyfoot{}
	\fancyfoot[C]{\thepage}
}
\pagestyle{headings}

\renewcommand{\sectionmark}[1]{
	\markboth{#1}{#1}
}


% --------------------------------
% Set default list style
% --------------------------------
\setlist[itemize,1]{topsep=2pt,label=\small$\bullet$, leftmargin=28pt}
\setlist[itemize,2]{topsep=2pt,leftmargin=18pt}
\setlist[itemize,3]{topsep=2pt,leftmargin=18pt}

\setlist[enumerate,1]{topsep=2pt,leftmargin=24pt}
\setlist[enumerate,2]{topsep=2pt,leftmargin=16pt}
\setlist[enumerate,3]{topsep=2pt,leftmargin=16pt}

% Podpis "Źródło"
\newcommand{\source}[1]{\setlength{\abovecaptionskip}{-5pt}\caption*{Źródło: {#1}} }


% ############################### COMPILER ##################################
%--------------------------------------
% PdfTeX specific configuration
%--------------------------------------
\ifpdf
    \RequirePackage[T1]{fontenc}
    \RequirePackage[utf8]{inputenc}
    \RequirePackage[
        protrusion=true,
        expansion=true
    ]{microtype}
\fi

%--------------------------------------
% XeTeX specific configuration
%--------------------------------------
\ifxetex
    % produces errors
    % \RequirePackage{fontspec-xetex}
    \RequirePackage[
        protrusion=true,
    ]{microtype}
\fi

%--------------------------------------
% LuaTeX specific configuration
%--------------------------------------
\ifluatex
    \RequirePackage[T1]{fontenc}
    \RequirePackage[utf8]{luainputenc}
    \RequirePackage{luatexbase}
    \RequirePackage{luacode}
    \RequirePackage[
        protrusion=true,
        expansion=true
    ]{microtype}
    % Silence "Package microtype Warning: Unknown slot number of character"
    % https://tex.stackexchange.com/questions/380812/microtype-warning-unknown-slot-number-of-character-with-lato-font
    \def\MT@warn@unknown{}
    % In LuaTeX, we can prevent one-letter words
    % from beging at the end of the line.
    \begin{luacode}

    local debug = false

    local glyph_id = node.id "glyph"
    local glue_id  = node.id "glue"
    local hlist_id = node.id "hlist"

    local prevent_single_letter = function (head)
        -- Polish prepositions that should not be orphaned
        local preposition_list = {
          "z", "do", "to", "na", "bez", "za", "pod", "u", "w", 
          "nad", "o", "od", "po", "czy", "że", "i", "lub", "albo", "przed"
        }
        
        -- Convert list to lookup table for O(1) access
        local prepositions = {}
        for _, prep in ipairs(preposition_list) do
            prepositions[prep] = true
        end
        
        local function collect_word(start_node)
            local word = ""
            local current = start_node
            local last_glyph = start_node
            
            while current do
                if current.id == glyph_id then
                    if unicode.utf8.match(unicode.utf8.char(current.char),"%a") then
                        word = word .. unicode.utf8.char(current.char)
                        last_glyph = current
                        current = current.next
                    else
                        -- Non-letter glyph, stop collecting
                        break
                    end
                elseif current.id == glue_id then
                    -- Space/glue, stop collecting
                    break
                else
                    -- Other node types (kern, penalty, etc.) - skip but continue
                    current = current.next
                end
            end
            return word:lower(), current, last_glyph
        end
        
        while head do
            if head.id == glyph_id then
                if unicode.utf8.match(unicode.utf8.char(head.char),"%a") then     -- is a letter
                    -- Check if this is truly the start of a word (not preceded by another letter)
                    local is_word_start = false
                    if not head.prev then
                        is_word_start = true  -- Start of node list
                    elseif head.prev.id == glue_id then
                        is_word_start = true  -- After a space
                    elseif head.prev.id == glyph_id then
                        -- Check if previous glyph is NOT a letter
                        if not unicode.utf8.match(unicode.utf8.char(head.prev.char),"%a") then
                            is_word_start = true
                        end
                    else
                        is_word_start = true  -- After some other node type
                    end
                    
                    if is_word_start then
                        local word, node_after, last_letter = collect_word(head)
                        

                            -- Debug: print word for inspection
                            if debug then
                                local prev_info = "nil"
                                if head.prev then
                                    prev_info = "id:" .. head.prev.id
                                end
                                texio.write_nl("Found word: '" .. word .. "' (length: " .. unicode.utf8.len(word) .. ", prev: " .. prev_info .. ")")
                            end

                        -- Check if word is followed by glue (space)
                        if node_after and node_after.id == glue_id then
                            local is_orphan = false
                            
                            
                            -- Check for single letter
                            if unicode.utf8.len(word) == 1 then
                                is_orphan = true
                            end
                            
                            -- Check for prepositions
                            if prepositions[word] then
                                is_orphan = true
                                if debug then
                                    texio.write_nl("  -> Matched as preposition!")
                                end
                            end
                            
                            if is_orphan then
                                local p = node.new("penalty")
                                p.penalty = 10000

                                if debug then
                                    local w = node.new("whatsit","pdf_literal")
                                    w.data = "q 1 0 1 RG 1 0 1 rg 0 0 m 0 5 l 2 5 l 2 0 l b Q"
                                    node.insert_after(head,last_letter,w)
                                    node.insert_after(head,w,p)
                                else
                                    node.insert_after(head,last_letter,p)
                                end
                            end
                        end
                        -- Skip to the node after the word we just processed
                        head = node_after
                    else
                        head = head.next
                    end
                else
                    head = head.next
                end
            else
                head = head.next
            end
        end
        return true
    end

    luatexbase.add_to_callback("pre_linebreak_filter",prevent_single_letter,"~")

    \end{luacode}
\fi

\endinput

