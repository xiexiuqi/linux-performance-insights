"""
测试数据生成器 - 用于快速测试报告格式
"""
from datetime import datetime


def generate_mock_data():
    """生成模拟数据用于测试"""
    
    mock_items = [
        {
            'source': 'LKML',
            'title': '[PATCH v3] sched/fair: Optimize select_idle_sibling() for large systems',
            'author': 'Peter Zijlstra',
            'url': 'https://lkml.org/lkml/2025/3/1/1',
            'content': 'This patch optimizes the select_idle_sibling() function...',
            'type': 'perf',
            'ai_summary': '优化调度器的空闲CPU选择算法，在大规模系统（>100核）上可减少20-30%的调度延迟。通过改进搜索策略，避免遍历所有CPU，显著提升性能。',
            'ai_tags': ['perf', 'scheduler', 'smp'],
        },
        {
            'source': 'LKML',
            'title': '[PATCH] mm/page_alloc: Fix memory leak in alloc_pages_bulk_array',
            'author': 'Vlastimil Babka',
            'url': 'https://lkml.org/lkml/2025/3/1/2',
            'content': 'Fix a memory leak in the bulk page allocation path...',
            'type': 'bugfix',
            'ai_summary': '修复批量页面分配路径中的内存泄漏问题。在高内存压力场景下，该泄漏可能导致系统内存逐渐耗尽。建议所有使用 bulk allocation 的系统应用此补丁。',
            'ai_tags': ['bugfix', 'memory', 'mm'],
        },
        {
            'source': 'Git Mainline',
            'title': 'Merge tag \'for-linus-6.9-rc1\' of git://git.kernel.org/.../bpf',
            'author': 'Linus Torvalds',
            'url': 'https://git.kernel.org/...',
            'commit_id': 'a1b2c3d4',
            'content': 'BPF updates for 6.9-rc1...',
            'type': 'feature',
            'ai_summary': '合并 BPF 子系统更新，包含新的 tracing 功能、性能优化和 bug 修复。新增支持在用户态程序中更细粒度的性能监控。',
            'ai_tags': ['feature', 'ebpf', 'tracing'],
        },
        {
            'source': 'LKML',
            'title': '[PATCH RFC] Introduce new io_uring ring buffer API',
            'author': 'Jens Axboe',
            'url': 'https://lkml.org/lkml/2025/3/1/4',
            'content': 'This RFC introduces a new ring buffer API for io_uring...',
            'type': 'feature',
            'ai_summary': 'io_uring 新提案：引入环形缓冲区 API，旨在简化异步 I/O 编程模型。提供更直观的接口，降低使用门槛，同时保持高性能。目前处于 RFC 阶段，欢迎社区反馈。',
            'ai_tags': ['feature', 'io', 'io_uring'],
        },
        {
            'source': 'Git Mainline',
            'title': 'x86/mm: Optimize TLB flush operations in munmap',
            'author': 'Dave Hansen',
            'url': 'https://git.kernel.org/...',
            'commit_id': 'e5f6g7h8',
            'content': 'Optimize TLB flushes...',
            'type': 'perf',
            'ai_summary': '优化 x86 架构 munmap 操作中的 TLB 刷新，通过延迟刷新和批量处理，在高频内存映射/解除映射场景下提升15-25%性能。',
            'ai_tags': ['perf', 'x86', 'memory', 'tlb'],
        },
        {
            'source': 'LKML',
            'title': '[PATCH] net: tcp: Fix race condition in tcp_recvmsg',
            'author': 'Eric Dumazet',
            'url': 'https://lkml.org/lkml/2025/3/1/6',
            'content': 'Fix a race in tcp receive path...',
            'type': 'bugfix',
            'ai_summary': '修复 TCP 接收路径中的竞态条件，该问题在高并发网络应用中可能导致数据包丢失或重复。建议网络密集型应用升级。',
            'ai_tags': ['bugfix', 'network', 'tcp'],
        },
        {
            'source': 'Git Mainline',
            'title': 'fs/ext4: Add support for fast commits',
            'author': 'Theodore Ts\'o',
            'url': 'https://git.kernel.org/...',
            'commit_id': 'i9j0k1l2',
            'content': 'Implement fast commit support...',
            'type': 'feature',
            'ai_summary': 'ext4 文件系统新增快速提交支持，显著减少 fsync 延迟。对于数据库等需要频繁同步的应用，性能可提升 2-5 倍。',
            'ai_tags': ['feature', 'filesystem', 'ext4'],
        },
        {
            'source': 'LKML',
            'title': '[PATCH v2] kernel: Improve printk performance with buffered output',
            'author': 'John Ogness',
            'url': 'https://lkml.org/lkml/2025/3/1/8',
            'content': 'Improve printk performance...',
            'type': 'perf',
            'ai_summary': '优化内核打印函数 printk 的性能，引入缓冲输出机制。在高日志量场景下减少锁竞争，提升系统响应速度。',
            'ai_tags': ['perf', 'printk', 'kernel'],
        },
        {
            'source': 'Git Mainline',
            'title': 'security/selinux: Fix label caching issue',
            'author': 'Paul Moore',
            'url': 'https://git.kernel.org/...',
            'commit_id': 'm3n4o5p6',
            'content': 'Fix a caching bug in SELinux...',
            'type': 'bugfix',
            'ai_summary': '修复 SELinux 标签缓存问题，该 bug 可能导致安全策略更新后缓存未失效，造成安全策略绕过风险。',
            'ai_tags': ['bugfix', 'security', 'selinux'],
        },
        {
            'source': 'LKML',
            'title': '[PATCH] Documentation: Update kernel debugging guide',
            'author': 'Jonathan Corbet',
            'url': 'https://lkml.org/lkml/2025/3/1/10',
            'content': 'Update the kernel debugging documentation...',
            'type': 'other',
            'ai_summary': '更新内核调试文档，补充 eBPF、ftrace 等新调试工具的使用说明，新增性能分析最佳实践章节。',
            'ai_tags': ['docs', 'debugging'],
        },
    ]
    
    return mock_items


if __name__ == '__main__':
    data = generate_mock_data()
    print(f"Generated {len(data)} mock items")
    for item in data:
        print(f"- [{item['type']}] {item['title'][:50]}...")

