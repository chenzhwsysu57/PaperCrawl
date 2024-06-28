#!/bin/bash

# 定义关键词列表
keywords_list=(
    'narcotics' 'tramadol' 'morphine' 'fentanyl' 'benzodiazepines'
    'diazepam' 'midazolam' 'dexme detomidine' 'atropine' 'penehyclidine hydrochloride'
    'cimetidine' 'ranitidine' 'proton pump inhibitors, PPI'
    'omeprazole, lansoprazole, pantoprazole, rabeprazole, esomeprazole'
    'regional anesthesia' 'peripheral nerve blocks, PNB' 'cervical plexus block'
    'superficial cervical plexus block' 'deep cervical plexus block'
    'complications of cervical plexus block' 'local anesthetic toxicity'
    'high spinal or total spinal anesthesia' 'phrenic nerve block'
    'recurrent laryngeal nerve block' 'vertebral artery injury causing bleeding, hematoma'
    'Horner syndrome' 'brachial plexus block' 'interscalene brachial plexus block'
    'supraclavicular brachial plexus block' 'axillary brachial plexus block'
    'transversus abdominis plane (TAP) block' 'paravertebral block (PVB)'
    'lower extremity nerve blocks' 'spinal and epidural anesthesia'
    'lumbar plexus block (psoas compartment block)' 'femoral nerve block' 'sciatic nerve block'
    'intrathecal anesthesia' 'spinal anesthesia' 'epidural anesthesia (including low-dose epidural)'
    'combined spinal-epidural anesthesia (CSEA)' 'saddle anesthesia (SA)' 'levobupivacaine' 'ropivacaine' 'bupivacaine' 'tetracaine'
)

# # 循环遍历每个关键词并在新的终端标签页中运行脚本
# for keyword in "${keywords_list[@]}"; do
#     osascript -e "tell application \"Terminal\" to do script \"python crawlpubmed.py --pdfdir '/Volumes/Lexar1TB/PaperCrawl/PubMed/downloaded_pdfs/anaesthesiology/*.pdf' --endpage 1000 --keywords '$keyword'\""
# done
