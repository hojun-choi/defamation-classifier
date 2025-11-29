package com.defamation.backend.web;

import com.defamation.backend.service.ClassificationRequestService;
import com.defamation.backend.web.dto.ClassificationRequestDto;
import com.defamation.backend.web.dto.PageResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/classification-requests")
@RequiredArgsConstructor
public class ClassificationRequestController {

    private final ClassificationRequestService classificationRequestService;

    @GetMapping
    public PageResponse<ClassificationRequestDto> getClassificationRequests(
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size,
            @RequestParam(name = "q", required = false) String q
    ) {
        return classificationRequestService.searchRequests(q, page, size);
    }
}
