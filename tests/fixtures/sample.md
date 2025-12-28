サンプルドキュメント

このファイルは、PDFとMarkdownの相互変換ツール「dcv」のサンプルMarkdownです。

⽬次

1. 概要

2. 特徴

3. 使い⽅

4. コマンド例

5. 参考リンク

概要

dcvは、PDFとMarkdownの間で簡単に変換できるCLIツールです。Typerベースで設計されてお

り、依存性注⼊やプロトコルによる拡張性を備えています。

特徴

PDF→Markdown変換は markitdown を利⽤
Markdown→PDF変換は md-to-pdf （npmパッケージ）を利⽤
Google Chromeによる⾼品質なPDFレンダリング

シンプルなCLIコマンド設計

拡張性の⾼いサービスプロバイダ構成

使い⽅

PDFからMarkdownへ変換

dcv pdf2md input.pdf output.md

MarkdownからPDFへ変換

dcv md2pdf input.md output.pdf

コマンド例

# PDF→Markdown

dcv pdf2md ./docs/sample.pdf ./docs/sample.md

# Markdown→PDF

dcv md2pdf ./docs/sample.md ./docs/sample.pdf

参考リンク

markitdown

md-to-pdf

Typer

このサンプルはdcvの動作確認や変換結果のイメージ作成にご利⽤します。

