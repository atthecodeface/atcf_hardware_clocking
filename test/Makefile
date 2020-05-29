Q=@
CDL_REGRESS = ${CDL_ROOT}/libexec/cdl/cdl_regress.py

smoke:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} --package-dir regress:${SRC_ROOT}/python --suite-dir=python test_clocking
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} --package-dir regress:${SRC_ROOT}/python --suite-dir=python --only-tests '.*_0' test_clock_timer

.PHONY:regress
regress:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} --package-dir regress:${SRC_ROOT}/python --suite-dir=python test_clock_timer test_clocking
