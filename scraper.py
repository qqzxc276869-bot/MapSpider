import os
import time
import pandas as pd
from DrissionPage import ChromiumPage, ChromiumOptions

def scrape_baidu_maps(search_query: str, total_to_scrape: int = 20, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    log(f"🚀 [无感隐身模式] 初始化，搜索关键词: {search_query} | 目标数: {total_to_scrape}")
    
    scraped_data_dict = {}

    try:
        # 使用 DrissionPage 接管本地真实浏览器，彻底避免所有指纹及 WebDriver 封杀
        co = ChromiumOptions().set_local_port(9222)
        try:
            page = ChromiumPage(addr_or_opts=co)
        except Exception as e:
            log("❌ 启动浏览器失败！请检查您是否安装了 Chrome/Edge，并关闭所有已抢占 9222 端口的进程。")
            log(str(e))
            return
            
        # 开始全屏监听后台数据包 (只要包含 qt=s 就是主要的搜索接口)
        page.listen.start('map.baidu.com')
        
        log(f"🌍 访问百度地图主页并伪装真人搜索行为...")
        page.get("https://map.baidu.com/", retry=2)
        
        # 很多时候直接访问 URL 百度不会触发搜索请求包，必须“亲手”打字并点击按钮
        try:
            search_box = page.ele('#sole-input', timeout=5)
            search_box.clear()
            search_box.input(search_query)
            # 点击搜索按钮
            page.ele('#search-button').click()
            log(f"🤖 自动输入关键词并为您点击了搜索: {search_query}")
        except Exception as e:
            log("⚠️ 自动输入搜索词失败，极小概率网络延迟，请手动在浏览器回车搜索。")
        
        log("⏳ 已部署网络间谍监听，正在等待商户 JSON 密文包掉落...")
        
        empty_checks = 0
        page_num = 1
        
        while len(scraped_data_dict) < total_to_scrape and empty_checks < 4:
            
            # 等待并拦截底层返回的一条数据包 (超时5秒)
            packet = page.listen.wait(timeout=5)
            
            if packet:
                try:
                    data = packet.response.body
                    # 匹配包含商户列表数据的字典
                    if isinstance(data, dict) and "content" in data and isinstance(data["content"], list):
                        for item in data["content"]:
                            name = item.get("name", "")
                            addr = item.get("addr", "")
                            tel = item.get("tel", "")
                            
                            if not tel and "ext" in item and isinstance(item["ext"], dict):
                                detail = item["ext"].get("detail_info", {})
                                tel = detail.get("phone", "") or detail.get("tel", "")
                            
                            if name and name not in scraped_data_dict:
                                scraped_data_dict[name] = {
                                    "商户名称": name,
                                    "联系电话": str(tel).replace(',', ' / ') if tel else "无公开电话",
                                    "详细地址": addr
                                }
                                current_count = len(scraped_data_dict)
                                log(f"✅ ({current_count}/{total_to_scrape}) {name} | 📞: {tel}")
                                
                                if current_count >= total_to_scrape:
                                    break
                        empty_checks = 0  # 收到了真实数据包，解除翻页空挡重试状态
                except Exception:
                    pass
            else:
                # 连续没收到数据包，可能数据已经加载完需要翻页
                if len(scraped_data_dict) > 0:
                    empty_checks += 1
            
            # 停止逻辑
            if len(scraped_data_dict) >= total_to_scrape:
                break
                
            # 翻页逻辑 - 增强版模糊匹配
            if packet is False or empty_checks >= 1:
                try:
                    # 尝试多种匹配模式，适配百度可能出现的 "下一页", "下一页>", "下一页 >" 等情况
                    # 使用 @text():下一页 表示包含 "下一页" 即可
                    next_btn = page.ele('tag:a@@text():下一页', timeout=2)
                    
                    if next_btn and "disabled" not in str(next_btn.attr("class")):
                        log(f"🔄 当前页数据已捕获，尝试点击下一页 (第 {page_num+1} 页)...")
                        
                        # 确保滚动到侧边栏底部以触发元素显示
                        page.scroll.to_bottom()
                        time.sleep(1)
                        
                        # 点击翻页
                        next_btn.click(by_js=True) # 使用 JS 点击更稳，防止被遮挡
                        page_num += 1
                        time.sleep(2)
                    else:
                        if empty_checks >= 2:
                            log("✅ 采集目标已完成或没有更多分页。")
                            break
                except Exception as e:
                    pass

        try:
            page.quit()
        except:
            pass
            
        final_data = list(scraped_data_dict.values())
        if final_data:
            final_data = final_data[:total_to_scrape]
            df = pd.DataFrame(final_data)
            os.makedirs("output", exist_ok=True)
            timestamp = int(time.time())
            filename = os.path.abspath(f"output/纯本地无感线索_{timestamp}.csv")
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            log(f"🎉 破解风控成功！无验证码硬核截获 {len(final_data)} 条商户数据，已保存至:")
            log(filename)
        else:
            log("🤷‍♂️ 未截获有效数据包，可能该地区没有该类商家结果。")
            
    except Exception as general_error:
        log(f"🔥 程序严重崩溃: {str(general_error)}")
