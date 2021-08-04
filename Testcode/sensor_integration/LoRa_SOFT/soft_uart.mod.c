#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x945918ef, "module_layout" },
	{ 0x3ce4ca6f, "disable_irq" },
	{ 0xf9a482f9, "msleep" },
	{ 0x92da6897, "param_ops_int" },
	{ 0xaa152108, "hrtimer_active" },
	{ 0x5cc2a511, "hrtimer_forward" },
	{ 0x695bf5e9, "hrtimer_cancel" },
	{ 0x47229b5c, "gpio_request" },
	{ 0x506c4db7, "gpio_to_desc" },
	{ 0xb43f9365, "ktime_get" },
	{ 0xb1ad28e0, "__gnu_mcount_nc" },
	{ 0xd179418a, "tty_register_driver" },
	{ 0x67ea780, "mutex_unlock" },
	{ 0x9ba148be, "put_tty_driver" },
	{ 0xa070eb55, "tty_set_operations" },
	{ 0xec523f88, "hrtimer_start_range_ns" },
	{ 0xc56baa68, "__tty_insert_flip_char" },
	{ 0xe346f67a, "__mutex_init" },
	{ 0xc5850110, "printk" },
	{ 0x1df9c359, "tty_port_init" },
	{ 0xc271c3be, "mutex_lock" },
	{ 0xdf5bd4a2, "gpiod_direction_input" },
	{ 0xb0646c4e, "gpiod_direction_output_raw" },
	{ 0x92d5838e, "request_threaded_irq" },
	{ 0x2196324, "__aeabi_idiv" },
	{ 0x6acb4344, "gpiod_set_debounce" },
	{ 0x67b27ec1, "tty_std_termios" },
	{ 0x1a02bbc7, "tty_unregister_driver" },
	{ 0xde829760, "__tty_alloc_driver" },
	{ 0xfe990052, "gpio_free" },
	{ 0x409873e3, "tty_termios_baud_rate" },
	{ 0xfcec0987, "enable_irq" },
	{ 0xdc45b4a3, "tty_port_link_device" },
	{ 0x37cd9bfb, "gpiod_to_irq" },
	{ 0x2bfed8b0, "gpiod_set_raw_value" },
	{ 0xa362bf8f, "hrtimer_init" },
	{ 0x44f4461d, "tty_flip_buffer_push" },
	{ 0xb112538b, "gpiod_get_raw_value" },
	{ 0xc1514a3b, "free_irq" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "82D309CA253E1CEADB2E755");
